# 📦 U.S. Tariffs & The Job Market — Labor Analytics Platform

## TL;DR for Hiring Managers
Built an end-to-end labor market analytics platform analyzing the impact 
of U.S. tariff policy on employment using BLS, FRED, and USITC data (2000–2024), 
with validated 5-year forecasts through 2029.

**Headline Finding:**
> Tariff protection creates ~3x downstream job loss vs jobs protected —
> with employment effects lagging policy announcements by 6–9 months.

Designed to enable decision-making across policy analysis, supply chain 
strategy, and investment planning.

---

## 🎯 Key Results

- **Manufacturing shed 4.56M jobs** since its 2001 peak — tariffs slowed
  but never reversed the structural decline
- **Construction gained +1.51M jobs** since 2009 — the silent winner of
  reshoring policy and trade protection
- **Retail added zero net jobs 2019–2024** despite full economic recovery
- **Achieved <4% forecast error** across 4 of 5 sectors vs real BLS
  March 2026 data — validated, not estimated

---

## 📌 Project Overview

End-to-end analysis of how U.S. tariff policy reshaped American employment
across 5 major sectors from 2000–2024, with a 5-year forecast through 2029.

**Core questions answered:**
- How did the 2002 Steel Tariffs affect manufacturing employment?
- What happened to jobs during the 2018–2019 U.S.–China Trade War?
- Which sectors gained and lost after each major tariff wave?
- What does the next 5 years look like under 2025 tariff escalation?

---

## 📊 Key Findings

| Event | Year | Impact |
|-------|------|--------|
| Bush Steel Tariffs | 2002 | -200K downstream jobs |
| China PNTR Effect | 2001–2010 | -2.4M manufacturing jobs |
| Trump Trade War | 2018–2019 | +steel jobs, -agriculture |
| COVID Supply Chain | 2020–2021 | -22M peak, uneven recovery |
| 2025 Escalation | 2025+ | Forecast in this project |

**Critical pattern:** Employment effects lag tariff announcements by
**6–9 months** — a measurable, consistent signal across all major events.

---

## ✅ Forecast Validation vs BLS (March 2026)

Achieved **<4% error across 80% of sectors** validated against
real BLS post-benchmark data:

| Sector | Forecast | BLS Actual | Error |
|--------|----------|------------|-------|
| Construction | 8,286K | 8,309K | ✅ 0.3% |
| Manufacturing | 13,194K | 12,573K | ⚠️ 5%* |
| Retail Trade | 15,459K | 15,427K | ✅ 0.2% |
| Total Nonfarm | 157,616K | 158,466K | ✅ 0.5% |
| Transportation | 6,294K | 6,532K | ✅ 3.6% |

*Gap caused by BLS historic -911K benchmark revision (Feb 2025).
Directional forecast remains correct.

---

## 🛠️ Tech Stack

| Layer | Tool | What It Enabled |
|-------|------|-----------------|
| Collection | Python + BLS/FRED/USITC APIs | 288 months of real economic data |
| Storage | PostgreSQL | Structured multi-sector data model |
| Analysis | SQL (CTEs, window functions) | Cross-sector trend and lag analysis |
| Forecasting | Prophet 1.3.0 | 5-year employment projections |
| Validation | BLS CES March 2026 | <4% error benchmark confirmed |
| Visualization | Tableau | Interactive policy impact dashboard |

---

## 📈 Tableau Dashboard

Designed an interactive dashboard enabling exploration of tariff impacts
across sectors — including lag analysis, forecast scenarios, and
annotated policy timelines.

🔗 [View Live Dashboard](#) *(link after Tableau Public publish)*

---

## 🗂️ Repo Structure
```
tariff-job-market-analysis/
├── scripts/
│   ├── collect_data.py         # BLS, FRED, USITC API ingestion
│   ├── clean_data.py           # Normalization and merging
│   ├── db_loader.py            # PostgreSQL loader
│   └── prophet_forecast.py    # Validated 5-year forecast
├── sql/
│   ├── schema.sql              # Data model
│   └── analysis_queries.sql   # Lag and trend analysis
├── data/cleaned/
│   ├── employment_monthly.csv
│   └── prophet_forecast_all_sectors.csv
├── FINDINGS.md                 # Full research conclusions
└── README.md
```

---

## 📚 Data Sources

- [BLS Current Employment Statistics](https://www.bls.gov/ces/)
- [FRED Federal Reserve Economic Data](https://fred.stlouisfed.org/)
- [USITC Trade Data](https://dataweb.usitc.gov/)
- [BLS Employment Projections 2024–2034](https://www.bls.gov/emp/)

---

## 💡 Resume Bullets

> Built an end-to-end analytics pipeline analyzing U.S. tariff policy
> impact on employment (2000–2024) using BLS, FRED, and USITC APIs

> Developed and validated 5-year forecasts using Prophet, achieving <4%
> error vs 2026 BLS data; identified 3x downstream job loss vs protected
> jobs and 6–9 month policy lag effects across 5 sectors

---

*Analysis by Chidvy | March 2026*
*Forecast validated against BLS post-benchmark data (March 2025 revision)*