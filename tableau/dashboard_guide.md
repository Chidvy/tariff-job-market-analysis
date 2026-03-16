# 📊 Tableau Dashboard Build Guide
## Tariff Impact on U.S. Job Market (2000–2029)

---

## Data Sources to Connect
1. `master_dataset.csv` — main dataset (monthly, 2000–2024)
2. `forecast_2025_2029.csv` — AWS forecast output
3. `tariff_events.csv` — reference table for annotations

---

## Dashboard 1: The Big Picture (Overview)
**Title:** *"How U.S. Tariffs Reshaped the Job Market (2000–2024)"*

### Sheet 1 — Dual-Axis Line Chart
- **X-axis:** Date (monthly)
- **Left Y-axis:** Total Nonfarm Employment (blue line)
- **Right Y-axis:** Import Price Index (orange line)
- **Add:** Reference bands for each tariff event (use `tariff_events` table)
- **Add:** Annotations on key events (2002 steel, 2018 trade war, 2020 COVID, 2025 escalation)

### Sheet 2 — Manufacturing vs. China Imports
- **X-axis:** Year
- **Bar:** China imports in billions (gray)
- **Line overlay:** Manufacturing employment (red)
- **Story:** Shows the inverse relationship clearly

---

## Dashboard 2: Sector Winners & Losers
**Title:** *"Which Industries Win and Lose Under Tariffs?"*

### Sheet 3 — Heatmap
- **Rows:** Sectors (manufacturing, retail, transport, etc.)
- **Columns:** Years (2000–2024)
- **Color:** YoY employment % change (red = decline, green = growth)
- **Filter:** Tariff regime dropdown (High / Moderate / Low)

### Sheet 4 — Waterfall Chart: Job Impact per Tariff Event
- Use Q1 SQL results
- Each tariff event = one bar showing net manufacturing job change
- Color: red for negative, green for positive

---

## Dashboard 3: The 5-Year Forecast
**Title:** *"What Happens to Jobs 2025–2029?"*

### Sheet 5 — Fan Chart (Forecast with Confidence Intervals)
- Connect `forecast_2025_2029.csv`
- **X-axis:** Date (2020–2029, blend historical + forecast)
- **Line:** `forecast_mean`
- **Band:** `forecast_p10` to `forecast_p90` (shaded area = uncertainty)
- **Sector filter:** dropdown to switch between sectors
- **Color:** Historical = solid, Forecast = dashed

### Sheet 6 — Forecast Summary Cards
- KPI tiles: one per sector showing 2025 → 2029 projected change %
- Color code: green = growth, red = decline

---

## Dashboard 4: Tariff Event Deep Dive
**Title:** *"Anatomy of a Tariff Shock"*

### Sheet 7 — Before/After Bar Chart
- Select any tariff event via filter
- Show employment 6 months before, at event, 6 months after, 12 months after
- Highlight the lag effect

### Sheet 8 — Geographic Impact (if adding state-level data later)
- Choropleth map of U.S.
- Color = manufacturing job change % by state during selected tariff period

---

## Final Dashboard Layout Tips
- Use a **dark theme** (makes it look more professional and senior)
- Add a **navigation bar** across top with 4 dashboard tabs
- Include **source citations** at the bottom: BLS, FRED, USITC
- Add your **name and LinkedIn** in the footer
- Publish to **Tableau Public** and copy the embed link for your GitHub README

---

## Color Palette (Recommended)
```
Background:     #1a1a2e
Primary blue:   #4361ee
Accent orange:  #f77f00
Green (growth): #06d6a0
Red (decline):  #ef233c
Gray neutral:   #8d99ae
Text:           #edf2f4
```

---

## Interviewers Will Ask You About:
1. *"Why did you choose these sectors?"* → Data availability + policy relevance
2. *"How confident are you in the 5-year forecast?"* → Explain the p10/p90 confidence bands
3. *"What's the most surprising finding?"* → Have one ready (e.g., downstream job losses exceed protected jobs)
4. *"How would you improve this?"* → State-level data, import product categories, wage impact
