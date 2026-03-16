-- ============================================================
-- analysis_queries.sql
-- Key business insight queries for Tariff & Job Market project
-- These power your Tableau dashboard and tell the story!
-- ============================================================

\c tariff_jobs;

-- ─────────────────────────────────────────────
-- Q1: Employment change during each tariff event
-- Shows the net job impact per sector per tariff era
-- ─────────────────────────────────────────────
WITH tariff_periods AS (
    SELECT
        te.event,
        te.start_date,
        COALESCE(te.end_date, CURRENT_DATE) AS end_date,
        te.avg_tariff_rate
    FROM tariff_events te
),
employment_at_start AS (
    SELECT
        tp.event,
        tp.avg_tariff_rate,
        em.manufacturing  AS mfg_start,
        em.retail_trade   AS retail_start,
        em.transportation_warehousing AS transport_start,
        em.total_nonfarm  AS total_start
    FROM tariff_periods tp
    JOIN employment_monthly em
        ON em.date = DATE_TRUNC('month', tp.start_date)::DATE
),
employment_at_end AS (
    SELECT
        tp.event,
        em.manufacturing  AS mfg_end,
        em.retail_trade   AS retail_end,
        em.transportation_warehousing AS transport_end,
        em.total_nonfarm  AS total_end
    FROM tariff_periods tp
    JOIN employment_monthly em
        ON em.date = DATE_TRUNC('month', tp.end_date)::DATE
)
SELECT
    s.event,
    s.avg_tariff_rate,
    ROUND((e.mfg_end - s.mfg_start), 0)          AS manufacturing_jobs_change_k,
    ROUND((e.retail_end - s.retail_start), 0)     AS retail_jobs_change_k,
    ROUND((e.transport_end - s.transport_start), 0) AS transport_jobs_change_k,
    ROUND((e.total_end - s.total_start), 0)       AS total_nonfarm_change_k,
    ROUND(((e.total_end - s.total_start) / s.total_start) * 100, 2) AS pct_change_total
FROM employment_at_start s
JOIN employment_at_end e ON s.event = e.event
ORDER BY s.event;


-- ─────────────────────────────────────────────
-- Q2: Manufacturing jobs vs. China import volume — correlation view
-- Core question: do more China imports = fewer mfg jobs?
-- ─────────────────────────────────────────────
SELECT
    tf.year,
    ROUND(tf.imports_china_usd / 1e9, 2)   AS china_imports_billions,
    ROUND(AVG(em.manufacturing), 0)         AS avg_mfg_employment_k,
    ROUND(AVG(em.manufacturing_yoy_pct), 2) AS mfg_yoy_pct_change,
    ROUND(AVG(ti.import_price_index), 2)    AS avg_import_price_index
FROM trade_flows_annual tf
JOIN employment_monthly em  ON em.year = tf.year
JOIN trade_indicators   ti  ON ti.date = em.date
GROUP BY tf.year, tf.imports_china_usd
ORDER BY tf.year;


-- ─────────────────────────────────────────────
-- Q3: 6-month employment lag analysis after tariff events
-- Validates the hypothesis: employment moves 6-9 months after tariff changes
-- ─────────────────────────────────────────────
WITH monthly_tariff AS (
    SELECT
        date,
        year,
        month,
        tariff_pressure_score,
        manufacturing,
        LAG(tariff_pressure_score, 6)  OVER (ORDER BY date) AS tariff_score_6mo_ago,
        LAG(tariff_pressure_score, 9)  OVER (ORDER BY date) AS tariff_score_9mo_ago,
        LAG(tariff_pressure_score, 12) OVER (ORDER BY date) AS tariff_score_12mo_ago
    FROM master_dataset
)
SELECT
    date,
    tariff_pressure_score         AS current_tariff_score,
    tariff_score_6mo_ago,
    ROUND(manufacturing, 0)       AS manufacturing_k,
    ROUND(manufacturing - LAG(manufacturing, 6) OVER (ORDER BY date), 0) AS mfg_6mo_change
FROM monthly_tariff
WHERE tariff_score_6mo_ago IS NOT NULL
ORDER BY date;


-- ─────────────────────────────────────────────
-- Q4: Sector winners & losers — which sectors GREW during tariff periods?
-- ─────────────────────────────────────────────
SELECT
    year,
    ROUND(AVG(manufacturing), 0)                AS manufacturing_k,
    ROUND(AVG(transportation_warehousing), 0)   AS transport_warehousing_k,
    ROUND(AVG(retail_trade), 0)                 AS retail_k,
    ROUND(AVG(total_nonfarm), 0)                AS total_nonfarm_k,
    MAX(tariff_pressure_score)                  AS tariff_pressure_score,
    CASE
        WHEN MAX(tariff_pressure_score) >= 2 THEN 'High Tariff Period'
        WHEN MAX(tariff_pressure_score) = 1 THEN 'Moderate Tariff Period'
        ELSE 'Low Tariff Period'
    END AS tariff_regime
FROM master_dataset
GROUP BY year
ORDER BY year;


-- ─────────────────────────────────────────────
-- Q5: Trade balance and total employment — macro relationship
-- ─────────────────────────────────────────────
SELECT
    m.year,
    ROUND(AVG(m.trade_balance) / 1e9, 2)     AS avg_trade_balance_billions,
    ROUND(AVG(m.total_nonfarm), 0)            AS avg_total_employment_k,
    ROUND(AVG(m.import_price_index), 2)       AS avg_import_price_index,
    ROUND(AVG(m.manufacturing_yoy_pct), 2)    AS avg_mfg_yoy_pct
FROM master_dataset m
GROUP BY m.year
ORDER BY m.year;


-- ─────────────────────────────────────────────
-- Q6: COVID vs. Trade War — side-by-side job shock comparison
-- ─────────────────────────────────────────────
SELECT
    'Trade War 2018-2019' AS period,
    MIN(manufacturing)    AS min_mfg_jobs_k,
    MAX(manufacturing)    AS max_mfg_jobs_k,
    MAX(manufacturing) - MIN(manufacturing) AS mfg_range_k,
    MIN(total_nonfarm)    AS min_total_k,
    MAX(total_nonfarm)    AS max_total_k
FROM master_dataset
WHERE date BETWEEN '2018-03-01' AND '2019-12-01'

UNION ALL

SELECT
    'COVID Shock 2020' AS period,
    MIN(manufacturing),
    MAX(manufacturing),
    MAX(manufacturing) - MIN(manufacturing),
    MIN(total_nonfarm),
    MAX(total_nonfarm)
FROM master_dataset
WHERE date BETWEEN '2020-01-01' AND '2020-12-31'

UNION ALL

SELECT
    '2025 Tariff Escalation' AS period,
    MIN(manufacturing),
    MAX(manufacturing),
    MAX(manufacturing) - MIN(manufacturing),
    MIN(total_nonfarm),
    MAX(total_nonfarm)
FROM master_dataset
WHERE date >= '2025-01-01';


-- ─────────────────────────────────────────────
-- Q7: YoY Manufacturing job change ranked by year
-- Quick leaderboard for Tableau
-- ─────────────────────────────────────────────
SELECT
    year,
    ROUND(AVG(manufacturing_yoy_pct), 2) AS avg_mfg_yoy_pct,
    CASE
        WHEN AVG(manufacturing_yoy_pct) > 1  THEN 'Growth Year'
        WHEN AVG(manufacturing_yoy_pct) < -1 THEN 'Decline Year'
        ELSE 'Flat Year'
    END AS classification
FROM master_dataset
GROUP BY year
ORDER BY avg_mfg_yoy_pct DESC;
