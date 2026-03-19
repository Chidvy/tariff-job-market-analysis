"""
collect_data.py
Pulls tariff, trade, and employment data from:
- BLS API (employment by sector)
- FRED API (import/export price indexes)
- USITC DataWeb (tariff and trade flows)
- Census Bureau (trade in goods)
"""

import requests
import pandas as pd
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

BLS_API_KEY  = os.getenv("BLS_API_KEY")
FRED_API_KEY = os.getenv("FRED_API_KEY")
RAW_DIR      = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1.  BLS — Employment by Industry (CES)
# ─────────────────────────────────────────────
# Series IDs: https://www.bls.gov/ces/
BLS_SERIES = {
    "manufacturing":          "CES3000000001",
    "retail_trade":           "CES4200000001",
    "wholesale_trade":        "CES4100000001",
    "transportation_warehousing": "CES4300000001",
    "agriculture":            "CEU0500000001",
    "construction":           "CES2000000001",
    "total_nonfarm":          "CES0000000001",
}

def fetch_bls_data(series_dict: dict, start_year: str = "2000", end_year: str = "2024") -> pd.DataFrame:
    """Fetch multiple BLS series and return as a combined DataFrame."""
    url     = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers = {"Content-type": "application/json"}
    payload = {
        "seriesid":   list(series_dict.values()),
        "startyear":  start_year,
        "endyear":    end_year,
        "registrationkey": BLS_API_KEY or "",
    }

    print("📡 Fetching BLS employment data...")
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    data     = response.json()

    all_records = []
    id_to_name  = {v: k for k, v in series_dict.items()}

    for series in data.get("Results", {}).get("series", []):
        sector = id_to_name.get(series["seriesID"], series["seriesID"])
        for item in series["data"]:
            all_records.append({
                "sector":     sector,
                "year":       int(item["year"]),
                "period":     item["period"],
                "employment": float(item["value"]),
            })

    df = pd.DataFrame(all_records)
    if df.empty: return df
    df = df[df["period"].str.startswith("M")]
    df["month"] = df["period"].str[1:].astype(int)
    df["date"]  = pd.to_datetime(df[["year", "month"]].assign(day=1))
    df.drop(columns=["period", "month"], inplace=True)
    df.sort_values(["sector", "date"], inplace=True)
    df.to_csv(f"{RAW_DIR}/bls_employment.csv", index=False)
    print(f"   ✅ Saved {len(df)} rows → {RAW_DIR}/bls_employment.csv")
    return df


# ─────────────────────────────────────────────
# 2.  FRED — Import/Export Price Indexes + Tariff Proxies
# ─────────────────────────────────────────────
FRED_SERIES = {
    "import_price_index":        "IR",          # Import Price Index (All)
    "export_price_index":        "IQ",          # Export Price Index (All)
    "steel_import_price":        "PCU331110331110",  # Steel mill products PPI
    "manufacturing_ppi":         "PCUOMFGOMFG",
    "trade_balance":             "BOPGSTB",     # Trade Balance Goods & Services
    "china_imports":             "IMPCH",       # U.S. imports from China
}

def fetch_fred_data(series_dict: dict, start: str = "2000-01-01") -> pd.DataFrame:
    """Fetch FRED series via API."""
    base_url = "https://api.stlouisfed.org/fred/series/observations"
    all_dfs  = []

    print("📡 Fetching FRED economic indicators...")
    for name, series_id in series_dict.items():
        params = {
            "series_id":       series_id,
            "api_key":         FRED_API_KEY,
            "file_type":       "json",
            "observation_start": start,
        }
        try:
            r    = requests.get(base_url, params=params)
            obs  = r.json().get("observations", [])
            df   = pd.DataFrame(obs)[["date", "value"]]
            df["indicator"] = name
            df["value"]     = pd.to_numeric(df["value"], errors="coerce")
            df["date"]      = pd.to_datetime(df["date"])
            all_dfs.append(df)
            print(f"   ✅ {name}: {len(df)} observations")
            time.sleep(0.3)    # be kind to the API
        except Exception as e:
            print(f"   ⚠️  {name} failed: {e}")

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv(f"{RAW_DIR}/fred_indicators.csv", index=False)
    print(f"   ✅ Saved → {RAW_DIR}/fred_indicators.csv")
    return combined


# ─────────────────────────────────────────────
# 3.  USITC — U.S. Tariff & Trade Flow Data
# ─────────────────────────────────────────────
# USITC DataWeb API: https://dataweb.usitc.gov/
USITC_PARTNERS = {
    "China":  "5700",
    "Canada": "1220",
    "Mexico": "2010",
    "EU":     "4000",
}

USITC_YEARS = list(range(2000, 2025))

def fetch_usitc_data() -> pd.DataFrame:
    """Fetch import values by country from USITC DataWeb."""
    base_url = "https://dataweb.usitc.gov/trade/getAllDataYears"
    all_records = []

    print("📡 Fetching USITC trade flow data...")
    for country, partner_id in USITC_PARTNERS.items():
        for year in USITC_YEARS:
            params = {
                "flow":       "imports",
                "partner":    partner_id,
                "year":       year,
                "aggregate":  "year",
            }
            try:
                r    = requests.get(base_url, params=params, timeout=10)
                data = r.json()
                all_records.append({
                    "country": country,
                    "year":    year,
                    "imports_value_usd": data.get("value", None),
                })
                time.sleep(0.2)
            except Exception as e:
                print(f"   ⚠️  USITC {country} {year}: {e}")

    df = pd.DataFrame(all_records)
    df.to_csv(f"{RAW_DIR}/usitc_trade_flows.csv", index=False)
    print(f"   ✅ Saved {len(df)} rows → {RAW_DIR}/usitc_trade_flows.csv")
    return df


# ─────────────────────────────────────────────
# 4.  Tariff Events Reference Table (hand-coded)
# ─────────────────────────────────────────────
TARIFF_EVENTS = [
    {"event": "Bush Steel Tariffs",           "start_date": "2002-03-01", "end_date": "2003-12-01", "sectors_affected": "steel,auto,manufacturing",    "avg_tariff_rate": 30},
    {"event": "China PNTR / WTO Accession",   "start_date": "2001-12-01", "end_date": "2010-12-01", "sectors_affected": "manufacturing,textiles,electronics", "avg_tariff_rate": 5},
    {"event": "Trump Trade War Phase 1",      "start_date": "2018-03-01", "end_date": "2019-12-01", "sectors_affected": "steel,aluminum,agriculture,tech", "avg_tariff_rate": 25},
    {"event": "Trade War Phase 2 / COVID",    "start_date": "2020-01-01", "end_date": "2021-12-01", "sectors_affected": "all",                          "avg_tariff_rate": 19},
    {"event": "Biden Tariff Continuations",   "start_date": "2022-01-01", "end_date": "2024-12-01", "sectors_affected": "steel,chips,EVs",              "avg_tariff_rate": 25},
    {"event": "2025 Tariff Escalation",       "start_date": "2025-01-01", "end_date": None,         "sectors_affected": "consumer goods,chips,autos",   "avg_tariff_rate": 45},
]

def save_tariff_events():
    df = pd.DataFrame(TARIFF_EVENTS)
    df.to_csv(f"{RAW_DIR}/tariff_events.csv", index=False)
    print(f"   ✅ Saved tariff events → {RAW_DIR}/tariff_events.csv")
    return df


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 Starting data collection...\n")
    fetch_bls_data(BLS_SERIES, "2015", "2025")
    fetch_fred_data(FRED_SERIES)
    fetch_usitc_data()
    save_tariff_events()
    print("\n✅ All raw data collected! Run clean_data.py next.\n")
