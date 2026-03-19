"""
clean_data.py
Cleans and merges raw data into analysis-ready datasets.
Outputs:
  - data/cleaned/employment_monthly.csv
  - data/cleaned/trade_indicators_monthly.csv
  - data/cleaned/master_dataset.csv    ← used for SQL & Tableau
"""

import pandas as pd
import numpy as np
import os

RAW_DIR     = "data/raw"
CLEANED_DIR = "data/cleaned"
os.makedirs(CLEANED_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# 1. Clean BLS Employment Data
# ─────────────────────────────────────────────
def clean_employment(path: str = f"{RAW_DIR}/bls_employment.csv") -> pd.DataFrame:
    print("🧹 Cleaning BLS employment data...")
    df = pd.read_csv(path, parse_dates=["date"])

    # Remove nulls and negatives
    df = df.dropna(subset=["employment"])
    df = df[df["employment"] > 0]

    # Pivot: one row per date, one column per sector
    df_pivot = df.pivot_table(index="date", columns="sector", values="employment").reset_index()
    df_pivot.columns.name = None

    # Forward-fill any gaps (occasional BLS reporting delays)
    df_pivot = df_pivot.sort_values("date")
    df_pivot.ffill().bfill()
    # Add year/month columns
    df_pivot["year"]  = df_pivot["date"].dt.year
    df_pivot["month"] = df_pivot["date"].dt.month

    # YoY % change for each sector
    sector_cols = [c for c in df_pivot.columns if c not in ["date", "year", "month"]]
    for col in sector_cols:
        df_pivot[f"{col}_yoy_pct"] = df_pivot[col].pct_change(12) * 100

    df_pivot.to_csv(f"{CLEANED_DIR}/employment_monthly.csv", index=False)
    print(f"   ✅ {len(df_pivot)} rows → {CLEANED_DIR}/employment_monthly.csv")
    return df_pivot


# ─────────────────────────────────────────────
# 2. Clean FRED Indicator Data
# ─────────────────────────────────────────────
def clean_fred(path: str = f"{RAW_DIR}/fred_indicators.csv") -> pd.DataFrame:
    print("🧹 Cleaning FRED indicators...")
    df = pd.read_csv(path, parse_dates=["date"])

    df = df.dropna(subset=["value"])

    # Resample to monthly (some series are quarterly)
    df_pivot = df.pivot_table(index="date", columns="indicator", values="value")
    df_pivot = df_pivot.resample("MS").interpolate(method="linear").reset_index()
    df_pivot.columns.name = None

    df_pivot["year"]  = df_pivot["date"].dt.year
    df_pivot["month"] = df_pivot["date"].dt.month

    df_pivot.to_csv(f"{CLEANED_DIR}/trade_indicators_monthly.csv", index=False)
    print(f"   ✅ {len(df_pivot)} rows → {CLEANED_DIR}/trade_indicators_monthly.csv")
    return df_pivot


# ─────────────────────────────────────────────
# 3. Clean USITC Trade Flow Data
# ─────────────────────────────────────────────
def clean_usitc(path: str = f"{RAW_DIR}/usitc_trade_flows.csv") -> pd.DataFrame:
    print("🧹 Cleaning USITC trade data...")
    df = pd.read_csv(path)

    df = df.dropna(subset=["imports_value_usd"])
    df["imports_value_usd"] = pd.to_numeric(df["imports_value_usd"], errors="coerce")

    # Pivot by country
    df_pivot = df.pivot_table(index="year", columns="country", values="imports_value_usd").reset_index()
    df_pivot.columns = ["year"] + [f"imports_{c.lower()}_usd" for c in df_pivot.columns[1:]]

    # Add total imports column
    import_cols = [c for c in df_pivot.columns if c.startswith("imports_")]
    df_pivot["imports_total_usd"] = df_pivot[import_cols].sum(axis=1)

    df_pivot.to_csv(f"{CLEANED_DIR}/usitc_annual.csv", index=False)
    print(f"   ✅ {len(df_pivot)} rows → {CLEANED_DIR}/usitc_annual.csv")
    return df_pivot


# ─────────────────────────────────────────────
# 4. Build Master Dataset
# ─────────────────────────────────────────────
def build_master(emp_df, fred_df, usitc_df) -> pd.DataFrame:
    print("🔗 Building master dataset...")

    # Merge employment + FRED on date (monthly)
    master = pd.merge(emp_df, fred_df, on=["date", "year", "month"], how="left")

    # Merge USITC on year (annual, broadcast to all months)
    master = pd.merge(master, usitc_df, on="year", how="left")

    # Add tariff event flags
    tariff_events = {
        "bush_steel_tariffs":    ("2002-03-01", "2003-12-01"),
        "china_pntr_shock":      ("2001-12-01", "2010-12-01"),
        "trump_trade_war":       ("2018-03-01", "2019-12-01"),
        "covid_supply_crisis":   ("2020-01-01", "2021-12-01"),
        "biden_tariffs":         ("2022-01-01", "2024-12-01"),
        "tariff_escalation_2025":("2025-01-01", "2099-12-01"),
    }

    for event, (start, end) in tariff_events.items():
        mask = (master["date"] >= pd.Timestamp(start)) & (master["date"] <= pd.Timestamp(end))
        master[f"flag_{event}"] = mask.astype(int)

    # Create a composite "tariff pressure score" (sum of active flags)
    flag_cols = [c for c in master.columns if c.startswith("flag_")]
    master["tariff_pressure_score"] = master[flag_cols].sum(axis=1)

    # Null checks
    null_counts = master.isnull().sum()
    high_null = null_counts[null_counts > len(master) * 0.2]
    if not high_null.empty:
        print(f"   ⚠️  Columns with >20% nulls (consider dropping): {list(high_null.index)}")

    master.to_csv(f"{CLEANED_DIR}/master_dataset.csv", index=False)
    print(f"   ✅ Master dataset: {len(master)} rows × {len(master.columns)} columns")
    print(f"   ✅ Saved → {CLEANED_DIR}/master_dataset.csv")
    return master


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 Starting data cleaning pipeline...\n")
    emp_df   = clean_employment()
    fred_df  = clean_fred()
    usitc_df = clean_usitc()
    master   = build_master(emp_df, fred_df, usitc_df)

    print("\n📋 Master dataset preview:")
    print(master.head())
    print(f"\nShape: {master.shape}")
    print("\n✅ Done! Run db_loader.py to load into PostgreSQL.\n")
