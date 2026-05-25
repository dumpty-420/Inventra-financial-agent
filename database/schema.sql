-- Inventra Simple Schema (Better PostgreSQL version)
-- Drop in correct order (dependents first)
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS finance CASCADE;
DROP TABLE IF EXISTS forecasts CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;

-- Vendors
CREATE TABLE vendors (
    vendor_id TEXT PRIMARY KEY,
    name TEXT,
    lead_time_days INTEGER,
    unit_price NUMERIC(10,2),
    on_time_delivery_rate NUMERIC(5,2),
    quality_score NUMERIC(5,2),
    avg_delay_days NUMERIC(5,2),
    reliability_rating TEXT,
    return_acceptance_rate NUMERIC(5,2),
    total_shipments_last_year INTEGER,
    payment_terms_days INTEGER,
    bulk_discount_percent NUMERIC(5,2),
    min_order_qty INTEGER
);

-- Inventory
CREATE TABLE inventory (
    sku TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    region TEXT,
    qty INTEGER,
    reorder_threshold INTEGER,
    unit_cost NUMERIC(10,2),
    vendor_id TEXT REFERENCES vendors(vendor_id)
);

-- Finance transactions
CREATE TABLE finance (
    id INTEGER PRIMARY KEY,
    sku TEXT REFERENCES inventory(sku),
    date DATE,
    amount NUMERIC(12,2),
    type TEXT,
    region TEXT
);

-- Sales with weather data
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    date DATE,
    sku TEXT REFERENCES inventory(sku),
    qty INTEGER,
    revenue NUMERIC(12,2),
    region TEXT,
    temperature NUMERIC(5,2),
    rainfall NUMERIC(8,2),
    humidity NUMERIC(5,2),
    weather_condition TEXT
);

-- Tickets for actions
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    sku TEXT REFERENCES inventory(sku),
    reason TEXT,
    recommended_qty INTEGER,
    vendor_id TEXT REFERENCES vendors(vendor_id),
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation history for persistent memory
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_message TEXT,
    assistant_message TEXT,
    intent TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forecast tracking for accuracy evaluation
CREATE TABLE forecasts (
    id SERIAL PRIMARY KEY,
    forecast_date DATE NOT NULL,
    sku TEXT NOT NULL REFERENCES inventory(sku),
    predicted_demand INTEGER,
    predicted_weather TEXT,
    recommendation TEXT,
    actual_demand INTEGER,
    actual_weather TEXT,
    accuracy_score NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);