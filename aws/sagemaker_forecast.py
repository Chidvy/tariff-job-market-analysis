"""
sagemaker_forecast.py
Uses AWS SageMaker DeepAR+ to forecast employment trends
for the next 5 years (2025–2029) by sector.

Prerequisites:
  - AWS account with SageMaker access
  - IAM role with SageMakerFullAccess + S3 access
  - Set AWS credentials in .env or via AWS CLI
"""

import boto3
import sagemaker
from sagemaker import get_execution_role
import pandas as pd
import numpy as np
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
REGION          = os.getenv("AWS_REGION", "us-east-1")
BUCKET          = os.getenv("S3_BUCKET", "tariff-job-market-forecasts")
PREFIX          = "deepar-employment"
ROLE_ARN        = os.getenv("SAGEMAKER_ROLE_ARN")   # IAM role ARN
PREDICTION_MONTHS = 60   # 5 years

SECTORS = [
    "manufacturing",
    "retail_trade",
    "transportation_warehousing",
    "construction",
    "wholesale_trade",
]

# ─────────────────────────────────────────────
# 1. Load cleaned data & prepare DeepAR format
# ─────────────────────────────────────────────
def load_and_prepare_data(csv_path: str = "data/cleaned/master_dataset.csv") -> dict:
    """Convert master dataset to DeepAR JSON-Lines format."""
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df = df.sort_values("date")

    train_records = []
    test_records  = []

    for sector in SECTORS:
        if sector not in df.columns:
            print(f"⚠️  Sector '{sector}' not found, skipping.")
            continue

        series = df[["date", sector, "tariff_pressure_score"]].dropna()

        # DeepAR requires: start, target, dynamic_feat (optional)
        train_end = "2023-12-01"
        train_df  = series[series["date"] <= train_end]
        full_df   = series.copy()

        train_record = {
            "start":        str(train_df["date"].min().date()),
            "target":       train_df[sector].round(2).tolist(),
            "dynamic_feat": [train_df["tariff_pressure_score"].tolist()],
            "cat":          [SECTORS.index(sector)],
        }

        # Test = full series (model will forecast beyond last point)
        test_record = {
            "start":        str(full_df["date"].min().date()),
            "target":       full_df[sector].round(2).tolist(),
            "dynamic_feat": [full_df["tariff_pressure_score"].tolist()],
            "cat":          [SECTORS.index(sector)],
        }

        train_records.append(train_record)
        test_records.append(test_record)

    return {"train": train_records, "test": test_records}


def save_jsonlines(records: list, path: str):
    """Save records to JSON-Lines format required by DeepAR."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"   ✅ Saved {len(records)} series → {path}")


# ─────────────────────────────────────────────
# 2. Upload to S3
# ─────────────────────────────────────────────
def upload_to_s3(local_path: str, s3_key: str, bucket: str = BUCKET):
    s3 = boto3.client("s3", region_name=REGION)
    try:
        s3.create_bucket(Bucket=bucket)
    except Exception:
        pass  # bucket exists
    s3.upload_file(local_path, bucket, s3_key)
    s3_uri = f"s3://{bucket}/{s3_key}"
    print(f"   ✅ Uploaded → {s3_uri}")
    return s3_uri


# ─────────────────────────────────────────────
# 3. Train DeepAR+ model on SageMaker
# ─────────────────────────────────────────────
def train_deepar(train_s3_uri: str, test_s3_uri: str) -> sagemaker.estimator.Estimator:
    session   = sagemaker.Session(boto3.Session(region_name=REGION))
    image_uri = sagemaker.image_uris.retrieve("forecasting-deepar", REGION)

    estimator = sagemaker.estimator.Estimator(
        image_uri         = image_uri,
        role              = ROLE_ARN,
        instance_count    = 1,
        instance_type     = "ml.c5.2xlarge",
        output_path       = f"s3://{BUCKET}/{PREFIX}/output",
        sagemaker_session = session,
    )

    hyperparameters = {
        "time_freq":              "M",            # monthly data
        "context_length":         "24",           # look back 24 months
        "prediction_length":      str(PREDICTION_MONTHS),
        "num_cells":              "64",
        "num_layers":             "3",
        "dropout_rate":           "0.10",
        "epochs":                 "200",
        "mini_batch_size":        "32",
        "learning_rate":          "0.001",
        "num_dynamic_feat":       "1",            # tariff_pressure_score
        "cardinality":            f"[{len(SECTORS)}]",
        "likelihood":             "gaussian",
        "early_stopping_patience":"20",
    }

    estimator.set_hyperparameters(**hyperparameters)

    print("🚀 Starting SageMaker DeepAR+ training job...")
    estimator.fit(
        inputs = {
            "train": sagemaker.TrainingInput(train_s3_uri, content_type="json"),
            "test":  sagemaker.TrainingInput(test_s3_uri,  content_type="json"),
        },
        job_name = f"tariff-jobs-deepar-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        wait     = True,
        logs     = True,
    )

    print(f"✅ Training complete! Model: {estimator.model_data}")
    return estimator


# ─────────────────────────────────────────────
# 4. Deploy endpoint & get predictions
# ─────────────────────────────────────────────
def deploy_and_predict(estimator, test_records: list) -> pd.DataFrame:
    print("🚀 Deploying SageMaker endpoint...")
    predictor = estimator.deploy(
        initial_instance_count = 1,
        instance_type          = "ml.m5.large",
        serializer             = sagemaker.serializers.JSONSerializer(),
        deserializer           = sagemaker.deserializers.JSONDeserializer(),
    )

    all_forecasts = []
    last_date = pd.Timestamp("2024-12-01")
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1),
                                   periods=PREDICTION_MONTHS, freq="MS")

    for i, record in enumerate(test_records):
        sector = SECTORS[i]
        print(f"   📡 Predicting: {sector}...")

        response = predictor.predict({
            "instances":   [record],
            "configuration": {
                "output_types": ["mean", "quantiles"],
                "quantiles":    ["0.1", "0.5", "0.9"],
            },
        })

        forecast = response["predictions"][0]
        mean_vals = forecast["mean"]
        p10_vals  = forecast["quantiles"]["0.1"]
        p90_vals  = forecast["quantiles"]["0.9"]

        for j, date in enumerate(forecast_dates):
            all_forecasts.append({
                "sector":       sector,
                "date":         date,
                "forecast_mean":round(mean_vals[j], 2),
                "forecast_p10": round(p10_vals[j],  2),
                "forecast_p90": round(p90_vals[j],  2),
            })

    # Cleanup endpoint (avoid charges!)
    predictor.delete_endpoint()
    print("✅ Endpoint deleted.")

    df_forecast = pd.DataFrame(all_forecasts)
    df_forecast.to_csv("data/cleaned/forecast_2025_2029.csv", index=False)
    print(f"✅ Saved forecasts → data/cleaned/forecast_2025_2029.csv")
    return df_forecast


# ─────────────────────────────────────────────
# 5. Summary: print key forecast insights
# ─────────────────────────────────────────────
def print_forecast_summary(df: pd.DataFrame):
    print("\n" + "="*60)
    print("📊 5-YEAR EMPLOYMENT FORECAST SUMMARY (2025–2029)")
    print("="*60)

    for sector in SECTORS:
        s = df[df["sector"] == sector]
        start = s["forecast_mean"].iloc[0]
        end   = s["forecast_mean"].iloc[-1]
        pct   = ((end - start) / start) * 100
        direction = "📈" if pct > 0 else "📉"
        print(f"\n{direction} {sector.replace('_', ' ').title()}")
        print(f"   2025 forecast: {start:,.0f}K jobs")
        print(f"   2029 forecast: {end:,.0f}K jobs")
        print(f"   Net change:    {pct:+.1f}%")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 Starting AWS SageMaker forecasting pipeline...\n")

    # 1. Prepare data
    datasets = load_and_prepare_data()
    save_jsonlines(datasets["train"], "data/raw/deepar_train.jsonl")
    save_jsonlines(datasets["test"],  "data/raw/deepar_test.jsonl")

    # 2. Upload to S3
    train_uri = upload_to_s3("data/raw/deepar_train.jsonl", f"{PREFIX}/train/train.json")
    test_uri  = upload_to_s3("data/raw/deepar_test.jsonl",  f"{PREFIX}/test/test.json")

    # 3. Train
    estimator = train_deepar(train_uri, test_uri)

    # 4. Predict
    df_forecast = deploy_and_predict(estimator, datasets["test"])

    # 5. Summary
    print_forecast_summary(df_forecast)

    print("\n✅ Done! Load forecast_2025_2029.csv into Tableau for visualization.\n")
