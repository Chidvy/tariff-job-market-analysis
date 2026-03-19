# U.S. Tariffs and the Job Market: Sector-Level Employment Analysis and Forecasting

## Summary

This project examines how major U.S. tariff episodes aligned with sector-level employment shifts using BLS, FRED, and USITC data.

I built an end-to-end labor-market analysis workflow covering **2015–2025**, with forecasts through **2030**, to test whether tariff-related protection supported durable job growth or instead contributed to more uneven sector outcomes beneath strong aggregate payroll numbers.

**Headline insight:** tariff-related protection appears to support select upstream industries, but broader labor-market effects remain mixed, unevenly distributed, and often delayed rather than immediate.

---

## Why this project matters

This project was built around a practical question:

**Do tariff-related policy shifts create durable labor-market strength, or do they redistribute job growth in ways that make the economy look stronger in aggregate than it is at the sector level?**

That matters for:

- policy analysis
- labor-market interpretation
- supply chain strategy
- business and investment decision-making

---

## Key findings

- **Manufacturing** remained structurally weak despite protection-focused policy support
- **Construction** appeared to benefit more than most sectors from reshoring and domestic investment dynamics
- **Retail Trade** showed weak net job growth despite broader recovery periods
- **Labor-market effects often appeared with a lag**, rather than immediately after major tariff episodes
- **Forecasts validated well against realized BLS data**, with forecast error below 4% in 4 of 5 sectors

---

## Main takeaway

Headline job growth can make the labor market look stronger than it really is.

This analysis suggests that tariff-related protection may support select upstream industries, but broader labor-market effects are more mixed. Employment gains appear unevenly distributed, and the impact on jobs often shows up with a lag rather than immediately after policy changes.

That means aggregate job numbers alone may not fully reflect what is happening underneath the surface.

**Bottom line:** the labor market may appear stable in aggregate while sector-level conditions tell a more fragile and uneven story.

---

## Scope of analysis

### Historical window
- **2015–2025**

### Forecast window
- **2026–2030**

### Sectors analyzed
- Manufacturing
- Construction
- Retail Trade
- Transportation & Warehousing
- Total Nonfarm Payrolls

### Policy episodes examined
- 2018–2019 U.S.–China Trade War
- 2020–2021 COVID and supply-chain disruption period
- 2025 tariff escalation as a forward-looking scenario context

---

## Methodology

I built a multi-step workflow using public economic data:

- collected labor-market and macroeconomic data from **BLS**, **FRED**, and **USITC**
- cleaned and standardized time-series data in **Python**
- stored structured datasets in **PostgreSQL**
- used **SQL** for trend, sector, and lag analysis
- generated five-year forecasts in **Prophet**
- validated forecast outputs against realized **BLS** data where available
- designed a **Tableau** dashboard to make findings easier to interpret

---

## Forecast validation

Forecast performance was checked against realized BLS data.

| Sector | Forecast | BLS Actual | Error |
|--------|----------|------------|-------|
| Construction | 8,286K | 8,309K | 0.3% |
| Manufacturing | 13,194K | 12,573K | 5.0%* |
| Retail Trade | 15,459K | 15,427K | 0.2% |
| Total Nonfarm | 157,616K | 158,466K | 0.5% |
| Transportation & Warehousing | 6,294K | 6,532K | 3.6% |

**Validation result:** forecast error remained below **4% in 4 of 5 sectors**, supporting the model’s usefulness for directional sector-level forecasting.

\* Manufacturing deviation was influenced by benchmark revision effects.

---

## Forward-looking insight

The labor market is not simply “strong” or “weak.”

What this project suggests is that job growth may be becoming more **uneven, concentrated, and policy-sensitive**.

In practical terms:

- some sectors benefit
- some sectors stagnate
- some sectors absorb delayed downstream pressure
- headline job growth can mask divergence underneath

---

## Tableau dashboard

The dashboard is designed to show:

- sector-level employment trends
- year-over-year change views
- forecast scenarios
- policy-event context
- labor-market comparison across sectors

**Live dashboard:** Tableau Public link coming soon

---

## Tech stack

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

- tariff episodes overlapped with other macroeconomic shocks, especially COVID and broader business-cycle effects
- sector-level employment data supports timing and association, not strict causal attribution
- forecasts assume a degree of structural continuity and may weaken under future shocks or major policy changes

These limitations strengthen the interpretation by making the analysis more rigorous and credible.

---

## Resume bullets

- Built an end-to-end labor-market analysis workflow using BLS, FRED, and USITC data to assess how major tariff episodes aligned with sector-level employment shifts from 2015–2025
- Developed and validated five-year sector forecasts in Prophet, achieving forecast error below 4% in 4 of 5 sectors against realized BLS data
- Identified uneven labor-market reallocation across sectors, showing how headline job growth can mask delayed downstream pressure and sector divergence
