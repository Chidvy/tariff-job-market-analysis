import pandas as pd
from prophet import Prophet
import os

df_raw = pd.read_csv("data/cleaned/employment_monthly.csv", parse_dates=["date"])

sectors = [
    "construction",
    "manufacturing",
    "retail_trade",
    "total_nonfarm",
    "transportation_warehousing"
]

all_forecasts = []

for sector in sectors:
    print(f"Forecasting {sector}...")
    df = df_raw[["date", sector]].dropna()
    df.columns = ["ds", "y"]

    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(df)

    future = m.make_future_dataframe(periods=60, freq="MS")
    forecast = m.predict(future)

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(60).copy()
    result.columns = ["date", "forecast_mean", "forecast_low", "forecast_high"]
    result["sector"] = sector
    all_forecasts.append(result)

final = pd.concat(all_forecasts, ignore_index=True)
final.to_csv("data/cleaned/prophet_forecast_all_sectors.csv", index=False)
print(f"Done! {len(final)} rows saved.")