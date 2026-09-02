# Footwear & Apparel Sales Analytics Dashboard

**Python · SQL · Power BI-style dashboard · Excel**

Analysis of 9,600+ footwear & apparel sales transactions (Adidas US Sales dataset schema) across product category, region, and sales channel (in-store, outlet, online) to surface performance trends and margin gaps.

> **Data note:** `data/adidas_us_sales.csv` is a **synthetic dataset generated to match the schema, scale, and statistical structure** of the public Kaggle "Adidas US Sales" dataset (same columns, retailers, regions, products, sales methods, and 2020–2021 date range). It was generated this way because this environment can't authenticate to Kaggle to pull the original file — every script here runs unchanged against the real Kaggle CSV if you drop it into `data/` with the same column names.

## Key finding

Sales-channel mix — not region — is the dominant driver of operating-margin variance. Outlet transactions run **14.0pp below** the 35.1% company-average margin (avg. discount ≈28% vs. ≈6% in-store); Online runs 2.0pp below. Regional discounting differences move margin by less than half a point. See [`docs/recommendations.md`](docs/recommendations.md) for the full leadership write-up.

## Project structure

```
data/
  adidas_us_sales.csv          Raw transaction-level data (9,648 rows)
  adidas_sales.db              SQLite database (loaded from the cleaned data)
  processed/                   Cleaned data + every aggregated table used downstream
scripts/
  01_generate_dataset.py       Synthetic dataset generator (matches Kaggle schema)
  02_clean_and_analyze.py      Pandas cleaning, validation, and aggregation
  03_load_sqlite.py            Loads cleaned data into SQLite for the SQL layer
  04_build_excel.py            Builds the Excel workbook (openpyxl)
sql/
  schema.sql                   Table definition (SQLite/Postgres/SQL Server compatible)
  analysis_queries.sql         9 analysis queries: KPIs, category/region/channel rollups,
                                margin-variance decomposition, monthly trend, top/bottom cuts
excel/
  Adidas_Sales_Analytics.xlsx  Raw data + live-formula pivot-style tables, KPI dashboard
                                with charts, and an editable what-if channel-mix model
dashboard/
  sales_dashboard.html         Interactive Power BI-style dashboard (standalone HTML)
docs/
  recommendations.md           Channel-mix & pricing recommendation for leadership
```

## How to reproduce

```bash
pip install pandas numpy openpyxl --break-system-packages

python scripts/01_generate_dataset.py     # -> data/adidas_us_sales.csv
python scripts/02_clean_and_analyze.py    # -> data/processed/*.csv
python scripts/03_load_sqlite.py          # -> data/adidas_sales.db
python scripts/04_build_excel.py          # -> excel/Adidas_Sales_Analytics.xlsx
```

Then run the queries in `sql/analysis_queries.sql` against `data/adidas_sales.db` with any SQLite client, and open `dashboard/sales_dashboard.html` in a browser for the interactive dashboard.

## Approach

1. **Clean & validate (Python/Pandas):** type coercion, de-duplication, null/negative-value checks, a referential check that `Total Sales ≈ Price per Unit × Units Sold`, and IQR-based outlier flagging (flagged, not dropped — legitimate bulk orders vary widely in this category).
2. **Aggregate & cross-validate (SQL + Excel):** the same category/region/channel rollups and the margin-variance decomposition are computed independently in SQLite and in Excel (live `SUMIFS`/`AVERAGEIFS` formulas, never hardcoded), and all three layers reconcile to the same figures (e.g., 35.14% overall operating margin, exact to the basis point across Python, SQL, and Excel).
3. **Decompose margin variance:** each channel's and region's operating margin is compared to the company average and weighted by revenue share, isolating how much each segment actually moves the company-level number — the method behind the "channel mix, not region" finding.
4. **Visualize (interactive dashboard):** KPI cards, a monthly revenue/margin trend line, category/region/channel drill-downs (click a bar or heatmap cell to filter), and a margin-variance driver chart — built as a standalone, filterable HTML page in place of a Power BI Desktop file (which can't run in this environment); the Excel workbook's pivot tables and what-if model are structured so the same model could be rebuilt in Power BI Desktop directly from `data/processed/clean_transactions.csv`.
5. **Recommend:** the findings are converted into a channel-mix and discount-discipline recommendation for leadership in `docs/recommendations.md`.

## Notes on the "Power BI dashboard"

This environment cannot run Power BI Desktop, so the dashboard is delivered as an interactive, filterable HTML page (`dashboard/sales_dashboard.html`) built on the same aggregated tables a Power BI report would use — KPI cards, trend lines, and category/region/channel drill-downs, matching the description's scope. To rebuild it in Power BI Desktop: import `data/processed/clean_transactions.csv`, build measures for Revenue (`SUM(Total Sales)`), Operating Margin % (`DIVIDE(SUM(Operating Profit), SUM(Total Sales))`), and Revenue Share % (`DIVIDE([Revenue], CALCULATE([Revenue], ALL(clean_transactions)))`), then replicate the visuals above using Category, Region, and Sales Method as slicers.
