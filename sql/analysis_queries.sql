-- analysis_queries.sql
-- Core analysis queries used to drive the dashboard and the leadership
-- recommendation. Written against the `sales_transactions` table created by
-- schema.sql and loaded by scripts/03_load_sqlite.py.

-- ---------------------------------------------------------------------
-- 1. Overall KPIs
-- ---------------------------------------------------------------------
SELECT
    ROUND(SUM(total_sales), 2)                                   AS total_revenue,
    ROUND(SUM(operating_profit), 2)                               AS total_operating_profit,
    ROUND(SUM(operating_profit) * 100.0 / SUM(total_sales), 2)    AS overall_operating_margin_pct,
    SUM(units_sold)                                                AS total_units_sold,
    COUNT(*)                                                       AS total_transactions
FROM sales_transactions;

-- ---------------------------------------------------------------------
-- 2. Revenue & margin by product category (Footwear vs Apparel)
-- ---------------------------------------------------------------------
SELECT
    category,
    ROUND(SUM(total_sales), 2)                                     AS revenue,
    ROUND(SUM(operating_profit), 2)                                AS operating_profit,
    ROUND(SUM(operating_profit) * 100.0 / SUM(total_sales), 2)      AS operating_margin_pct,
    ROUND(SUM(total_sales) * 100.0 / SUM(SUM(total_sales)) OVER (), 2) AS revenue_share_pct
FROM sales_transactions
GROUP BY category
ORDER BY revenue DESC;

-- ---------------------------------------------------------------------
-- 3. Revenue & margin by region
-- ---------------------------------------------------------------------
SELECT
    region,
    ROUND(SUM(total_sales), 2)                                     AS revenue,
    ROUND(SUM(operating_profit), 2)                                AS operating_profit,
    ROUND(SUM(operating_profit) * 100.0 / SUM(total_sales), 2)      AS operating_margin_pct
FROM sales_transactions
GROUP BY region
ORDER BY revenue DESC;

-- ---------------------------------------------------------------------
-- 4. Revenue & margin by sales channel (In-store / Outlet / Online)
--    -> This is the #1 driver of margin variance in the dataset.
-- ---------------------------------------------------------------------
SELECT
    sales_method,
    ROUND(SUM(total_sales), 2)                                     AS revenue,
    ROUND(SUM(total_sales) * 100.0 / SUM(SUM(total_sales)) OVER (), 2) AS revenue_share_pct,
    ROUND(SUM(operating_profit), 2)                                AS operating_profit,
    ROUND(SUM(operating_profit) * 100.0 / SUM(total_sales), 2)      AS operating_margin_pct
FROM sales_transactions
GROUP BY sales_method
ORDER BY revenue DESC;

-- ---------------------------------------------------------------------
-- 5. Region x Channel matrix -- surfaces regional discounting interacting
--    with channel mix (e.g. South + Outlet is the weakest margin cell)
-- ---------------------------------------------------------------------
SELECT
    region,
    sales_method,
    ROUND(SUM(total_sales), 2)                                     AS revenue,
    ROUND(SUM(operating_profit) * 100.0 / SUM(total_sales), 2)      AS operating_margin_pct
FROM sales_transactions
GROUP BY region, sales_method
ORDER BY operating_margin_pct ASC;

-- ---------------------------------------------------------------------
-- 6. Margin-variance decomposition: each channel's margin vs. the company
--    overall margin, weighted by revenue share (pp = percentage points)
-- ---------------------------------------------------------------------
WITH overall AS (
    SELECT SUM(operating_profit) * 100.0 / SUM(total_sales) AS overall_margin_pct
    FROM sales_transactions
),
by_channel AS (
    SELECT
        sales_method,
        SUM(total_sales) AS revenue,
        SUM(operating_profit) * 100.0 / SUM(total_sales) AS margin_pct
    FROM sales_transactions
    GROUP BY sales_method
)
SELECT
    c.sales_method,
    ROUND(c.revenue * 100.0 / (SELECT SUM(total_sales) FROM sales_transactions), 2) AS revenue_share_pct,
    ROUND(c.margin_pct, 2)                                            AS margin_pct,
    ROUND(c.margin_pct - o.overall_margin_pct, 2)                     AS margin_vs_overall_pp,
    ROUND((c.revenue * 100.0 / (SELECT SUM(total_sales) FROM sales_transactions)) / 100.0
          * (c.margin_pct - o.overall_margin_pct), 3)                 AS weighted_margin_contribution_pp
FROM by_channel c CROSS JOIN overall o
ORDER BY ABS(weighted_margin_contribution_pp) DESC;

-- ---------------------------------------------------------------------
-- 7. Top / bottom Retailer x Region combinations by margin
-- ---------------------------------------------------------------------
SELECT
    retailer,
    region,
    ROUND(SUM(total_sales), 2)                                     AS revenue,
    ROUND(SUM(operating_profit) * 100.0 / SUM(total_sales), 2)      AS operating_margin_pct
FROM sales_transactions
GROUP BY retailer, region
ORDER BY operating_margin_pct DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- 8. Monthly revenue & margin trend (for the trend-line visuals)
-- ---------------------------------------------------------------------
SELECT
    strftime('%Y-%m', invoice_date)                                AS month,
    sales_method,
    ROUND(SUM(total_sales), 2)                                     AS revenue,
    ROUND(SUM(operating_profit) * 100.0 / SUM(total_sales), 2)      AS operating_margin_pct
FROM sales_transactions
GROUP BY month, sales_method
ORDER BY month, sales_method;

-- ---------------------------------------------------------------------
-- 9. Average selling price & discounting proxy by channel and category
-- ---------------------------------------------------------------------
SELECT
    category,
    sales_method,
    ROUND(AVG(price_per_unit), 2)                                  AS avg_price_per_unit,
    ROUND(AVG(operating_margin) * 100, 2)                          AS avg_operating_margin_pct,
    SUM(units_sold)                                                AS total_units
FROM sales_transactions
GROUP BY category, sales_method
ORDER BY category, avg_operating_margin_pct DESC;
