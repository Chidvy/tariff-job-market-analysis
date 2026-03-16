-- ============================================================
-- schema.sql
-- Database schema for Tariff & Job Market Analysis
-- Run this BEFORE db_loader.py if you want explicit typing
-- ============================================================

CREATE DATABASE IF NOT EXISTS tariff_jobs;
\c tariff_jobs;

-- ─────────────────────────────────────────────
-- Employment by Sector (Monthly)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS employment_monthly (
    id                          SERIAL PRIMARY KEY,
    date                        DATE NOT NULL,
    year                        INT,
    month                       INT,
    manufacturing               NUMERIC(12,2),
    retail_trade                NUMERIC(12,2),
    wholesale_trade             NUMERIC(12,2),
    transportation_warehousing  NUMERIC(12,2),
    agriculture                 NUMERIC(12,2),
    construction                NUMERIC(12,2),
    total_nonfarm               NUMERIC(12,2),
    manufacturing_yoy_pct       NUMERIC(8,4),
    retail_trade_yoy_pct        NUMERIC(8,4),
    wholesale_trade_yoy_pct     NUMERIC(8,4)
);

CREATE INDEX idx_emp_date ON employment_monthly(date);
CREATE INDEX idx_emp_year ON employment_monthly(year);

-- ─────────────────────────────────────────────
-- Trade & Price Indicators (Monthly, from FRED)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trade_indicators (
    id                   SERIAL PRIMARY KEY,
    date                 DATE NOT NULL,
    year                 INT,
    month                INT,
    import_price_index   NUMERIC(10,4),
    export_price_index   NUMERIC(10,4),
    steel_import_price   NUMERIC(10,4),
    manufacturing_ppi    NUMERIC(10,4),
    trade_balance        NUMERIC(15,2),
    china_imports        NUMERIC(15,2)
);

CREATE INDEX idx_trade_date ON trade_indicators(date);

-- ─────────────────────────────────────────────
-- Trade Flows by Country (Annual, from USITC)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trade_flows_annual (
    id                      SERIAL PRIMARY KEY,
    year                    INT NOT NULL,
    imports_china_usd       BIGINT,
    imports_canada_usd      BIGINT,
    imports_mexico_usd      BIGINT,
    imports_eu_usd          BIGINT,
    imports_total_usd       BIGINT
);

CREATE INDEX idx_flows_year ON trade_flows_annual(year);

-- ─────────────────────────────────────────────
-- Tariff Events Reference Table
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tariff_events (
    id                  SERIAL PRIMARY KEY,
    event               VARCHAR(100) NOT NULL,
    start_date          DATE,
    end_date            DATE,
    sectors_affected    TEXT,
    avg_tariff_rate     NUMERIC(5,2)
);

-- ─────────────────────────────────────────────
-- Master Dataset (denormalized for Tableau)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS master_dataset (
    id                       SERIAL PRIMARY KEY,
    date                     DATE NOT NULL,
    year                     INT,
    month                    INT,
    -- Employment
    manufacturing            NUMERIC(12,2),
    retail_trade             NUMERIC(12,2),
    transportation_warehousing NUMERIC(12,2),
    total_nonfarm            NUMERIC(12,2),
    manufacturing_yoy_pct    NUMERIC(8,4),
    -- Trade indicators
    import_price_index       NUMERIC(10,4),
    trade_balance            NUMERIC(15,2),
    china_imports            NUMERIC(15,2),
    -- Tariff flags
    flag_bush_steel_tariffs      SMALLINT DEFAULT 0,
    flag_china_pntr_shock        SMALLINT DEFAULT 0,
    flag_trump_trade_war         SMALLINT DEFAULT 0,
    flag_covid_supply_crisis     SMALLINT DEFAULT 0,
    flag_biden_tariffs           SMALLINT DEFAULT 0,
    flag_tariff_escalation_2025  SMALLINT DEFAULT 0,
    tariff_pressure_score        SMALLINT DEFAULT 0
);

CREATE INDEX idx_master_date ON master_dataset(date);
CREATE INDEX idx_master_year ON master_dataset(year);
CREATE INDEX idx_master_tariff ON master_dataset(tariff_pressure_score);
