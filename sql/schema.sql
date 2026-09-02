-- schema.sql
-- Table definition for the cleaned Adidas US Sales transaction data.
-- Compatible with SQLite / PostgreSQL / SQL Server (minor type tweaks noted).

CREATE TABLE IF NOT EXISTS sales_transactions (
    transaction_id      INTEGER PRIMARY KEY AUTOINCREMENT,  -- SERIAL in Postgres, IDENTITY(1,1) in SQL Server
    retailer             TEXT NOT NULL,
    retailer_id           INTEGER NOT NULL,
    invoice_date          DATE NOT NULL,
    region                TEXT NOT NULL,
    state                 TEXT NOT NULL,
    city                  TEXT NOT NULL,
    product               TEXT NOT NULL,
    category              TEXT NOT NULL,             -- Footwear / Apparel
    price_per_unit        NUMERIC(10,2) NOT NULL,
    units_sold             INTEGER NOT NULL,
    total_sales             NUMERIC(12,2) NOT NULL,
    operating_profit        NUMERIC(12,2) NOT NULL,
    operating_margin        NUMERIC(6,4) NOT NULL,     -- decimal fraction, e.g. 0.3514 = 35.14%
    sales_method            TEXT NOT NULL              -- In-store / Outlet / Online
);

CREATE INDEX IF NOT EXISTS idx_sales_region     ON sales_transactions(region);
CREATE INDEX IF NOT EXISTS idx_sales_method     ON sales_transactions(sales_method);
CREATE INDEX IF NOT EXISTS idx_sales_category   ON sales_transactions(category);
CREATE INDEX IF NOT EXISTS idx_sales_date       ON sales_transactions(invoice_date);
