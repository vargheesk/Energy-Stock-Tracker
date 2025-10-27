-- ============================================
-- Energy Stock Tracker Database Schema
-- BEGINNER FRIENDLY VERSION
-- Copy and paste this entire file into Supabase SQL Editor
-- ============================================

-- Delete tables if they exist (start fresh)
DROP TABLE IF EXISTS stock_data;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS etl_log;

-- ============================================
-- Table 1: companies
-- This stores information about energy companies
-- ============================================
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add energy companies to the table
INSERT INTO companies (symbol, name, sector) VALUES
('XOM', 'Exxon Mobil Corporation', 'Oil & Gas'),
('BP', 'BP plc', 'Oil & Gas'),
('CVX', 'Chevron Corporation', 'Oil & Gas'),
('SHEL', 'Shell plc', 'Oil & Gas'),
('TTE', 'TotalEnergies SE', 'Oil & Gas'),
('COP', 'ConocoPhillips', 'Oil & Gas'),
('TSLA', 'Tesla Inc', 'Renewable Energy'),
('ENPH', 'Enphase Energy Inc', 'Renewable Energy'),
('NEE', 'NextEra Energy Inc', 'Renewable Energy'),
('FSLR', 'First Solar Inc', 'Renewable Energy');

-- ============================================
-- Table 2: stock_data
-- This stores daily stock prices and calculated values
-- ============================================
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    open_price FLOAT,
    high_price FLOAT,
    low_price FLOAT,
    close_price FLOAT NOT NULL,
    volume BIGINT,
    pct_change FLOAT,
    ma_7 FLOAT,
    ma_30 FLOAT,
    volatility FLOAT,
    trend VARCHAR(10),
    oil_price FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Table 3: etl_log
-- This tracks when ETL runs and if it was successful
-- ============================================
CREATE TABLE etl_log (
    id SERIAL PRIMARY KEY,
    run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rows_inserted INT DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    notes TEXT
);

-- ============================================
-- Test the tables - Run these queries to verify
-- ============================================

-- Check companies table
SELECT * FROM companies;

-- Check stock_data table (will be empty until ETL runs)
SELECT * FROM stock_data LIMIT 10;

-- Check etl_log table (will be empty until ETL runs)
SELECT * FROM etl_log;

-- ============================================
-- Done! Your database is ready
-- ============================================