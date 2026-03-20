# U.S. Tariffs and the Job Market: Sector-Level Employment Analysis and Forecasting

## Summary

This project examines how major U.S. tariff episodes aligned with sector-level employment shifts using **BLS**, **FRED**, and **USITC** data.

I built an end-to-end labor-market analysis workflow covering **2015–2025**, with forecasts through **2030**, to test whether tariff-related protection supported durable job growth or instead contributed to more uneven sector outcomes beneath strong aggregate payroll numbers.

**Headline Insight:** Tariff-related protection appears to support select upstream industries, but broader labor-market effects remain mixed, unevenly distributed, and often delayed rather than immediate.

---

## Why This Project Matters

This project was built around a practical question:

**Do tariff-related policy shifts create durable labor-market strength, or do they redistribute job growth in ways that make the economy look stronger in aggregate than it is at the sector level?**

That matters for:

- Policy Analysis
- Labor-Market Interpretation
- Supply Chain Strategy
- Business and Investment Decision-Making

---

## Key Findings

- **Manufacturing** remained structurally weak despite protection-focused policy support
- **Construction** appeared to benefit more than most sectors from reshoring and domestic investment dynamics
- **Retail Trade** showed weak net job growth despite broader recovery periods
- **Labor-Market Effects Often Appeared With a Lag**, rather than immediately after major tariff episodes
- **Forecasts Validated Well Against Realized BLS Data**, with forecast error below 4% in 4 of 5 sectors

---

## Main Takeaway

Headline job growth can make the labor market look stronger than it really is.

This analysis suggests that tariff-related protection may support select upstream industries, but broader labor-market effects are more mixed. Employment gains appear unevenly distributed, and the impact on jobs often shows up with a lag rather than immediately after policy changes.

That means aggregate job numbers alone may not fully reflect what is happening underneath the surface.

**Bottom Line:** The labor market may appear stable in aggregate while sector-level conditions tell a more fragile and uneven story.

---

## Scope of Analysis

### Historical Window
**2015–2025**

### Forecast Window
**2026–2030**

### Sectors Analyzed
- Manufacturing
- Construction
- Retail Trade
- Transportation & Warehousing
- Total Nonfarm Payrolls

### Policy Episodes Examined
- 2018–2019 U.S.–China Trade War
- 2020–2021 COVID and Supply-Chain Disruption Period
- 2025 Tariff Escalation as a Forward-Looking Scenario Context

---

## Methodology

I built a multi-step workflow using public economic data:

- Collected labor-market and macroeconomic data from **BLS**, **FRED**, and **USITC**
- Cleaned and standardized time-series data in **Python**
- Stored structured datasets in **PostgreSQL**
- Used **SQL** for trend, sector, and lag analysis
- Generated five-year forecasts in **Prophet**
- Validated forecast outputs against realized **BLS** data where available
- Designed a **Tableau** dashboard to make findings easier to interpret

---

## Forecast Validation

Forecast performance was checked against realized BLS data.

| Sector | Forecast | BLS Actual | Error |
|--------|----------|------------|-------|
| Construction | 8,286K | 8,309K | 0.3% |
| Manufacturing | 13,194K | 12,573K | 5.0%* |
| Retail Trade | 15,459K | 15,427K | 0.2% |
| Total Nonfarm | 157,616K | 158,466K | 0.5% |
| Transportation & Warehousing | 6,294K | 6,532K | 3.6% |

**Validation Result:** Forecast error remained below 4% in 4 of 5 sectors, supporting the model’s usefulness for directional sector-level forecasting.

\*Manufacturing deviation was influenced by benchmark revision effects.

---

## Forward-Looking Insight

The labor market is not simply “strong” or “weak.”

What this project suggests is that job growth may be becoming more **uneven, concentrated, and policy-sensitive**.

In practical terms:

- Some sectors benefit
- Some sectors stagnate
- Some sectors absorb delayed downstream pressure
- Headline job growth can mask divergence underneath

---

## Tableau Dashboard

The dashboard is designed to show:

- Sector-level employment trends
- Forecast scenarios
- Policy-event context
- Labor-market comparison across sectors

**Live Dashboard:** [View on Tableau Public](https://public.tableau.com/app/profile/chidvi.meduri/viz/USTariffs-Job-Market-Sector-Analysis/U_STariifsJobMarketSectorLevelEmploymentTrendsandForecasts?publish=yes)

---

## Tech Stack

- Python
- PostgreSQL
- SQL
- Prophet
- Tableau
- BLS / FRED / USITC APIs

---

## Limitations

This analysis does not claim that tariffs alone caused all labor-market changes.

Important limitations include:

- Tariff episodes overlapped with other macroeconomic shocks, especially COVID and broader business-cycle effects
- Sector-level employment data supports timing and association, not strict causal attribution
- Forecasts assume a degree of structural continuity and may weaken under future shocks or major policy changes


---




