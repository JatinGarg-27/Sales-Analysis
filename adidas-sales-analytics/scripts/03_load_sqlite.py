"""
03_load_sqlite.py

Loads the cleaned transaction data into a SQLite database
(data/adidas_sales.db) using sql/schema.sql, so sql/analysis_queries.sql can
be run and validated against a real SQL engine (portable to Postgres/SQL
Server/MySQL with only minor type syntax changes).
"""

import sqlite3
import pandas as pd

DB_PATH = "data/adidas_sales.db"
CLEAN_CSV = "data/processed/clean_transactions.csv"
SCHEMA_PATH = "sql/schema.sql"


def main():
    df = pd.read_csv(CLEAN_CSV, parse_dates=["Invoice Date"])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS sales_transactions")
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    load_df = pd.DataFrame({
        "retailer": df["Retailer"],
        "retailer_id": df["Retailer ID"],
        "invoice_date": df["Invoice Date"].dt.strftime("%Y-%m-%d"),
        "region": df["Region"],
        "state": df["State"],
        "city": df["City"],
        "product": df["Product"],
        "category": df["Category"],
        "price_per_unit": df["Price per Unit"],
        "units_sold": df["Units Sold"],
        "total_sales": df["Total Sales"],
        "operating_profit": df["Operating Profit"],
        "operating_margin": df["Operating Margin"],
        "sales_method": df["Sales Method"],
    })
    load_df.to_sql("sales_transactions", conn, if_exists="append", index=False)
    conn.commit()

    n = cur.execute("SELECT COUNT(*) FROM sales_transactions").fetchone()[0]
    print(f"Loaded {n:,} rows into {DB_PATH}")

    # quick validation: run the KPI query
    cur.execute("""
        SELECT ROUND(SUM(total_sales),2), ROUND(SUM(operating_profit)*100.0/SUM(total_sales),2)
        FROM sales_transactions
    """)
    rev, margin = cur.fetchone()
    print(f"Validation -> Total revenue: ${rev:,.2f} | Overall margin: {margin}%")

    conn.close()


if __name__ == "__main__":
    main()
