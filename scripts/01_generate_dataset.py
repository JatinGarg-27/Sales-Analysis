"""
01_generate_dataset.py

Generates a synthetic transaction-level footwear & apparel sales dataset that
mirrors the schema, scale, and statistical structure of the public Kaggle
"Adidas US Sales" dataset (retailer x region x product x sales-channel
transactions, Jan-2020 through Dec-2021).

NOTE: This is a synthetically generated dataset built to match the real
dataset's structure (same columns, retailers, regions, products, sales
methods, and realistic margin/discounting patterns). It is not a scrape or
copy of the original Kaggle file -- it exists so the rest of this project
(SQL, Excel, Power BI-style dashboard) is fully reproducible without needing
Kaggle credentials.

Output: data/adidas_us_sales.csv  (~9,600 rows)
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# Reference dimensions (mirrors the real Adidas US Sales dataset)
# ---------------------------------------------------------------------------

RETAILERS = {
    "Foot Locker": 1185732,
    "Walmart": 1197831,
    "Sports Direct": 1128299,
    "West Gear": 1189833,
    "Kohl's": 1197831 + 1,  # placeholder distinct id
    "Amazon": 1128299 + 1,
}
# fix duplicate collision
RETAILERS = {
    "Foot Locker": 1185732,
    "Walmart": 1197831,
    "Sports Direct": 1128299,
    "West Gear": 1189833,
    "Kohl's": 1197834,
    "Amazon": 1128302,
}

REGION_STATES_CITIES = {
    "Northeast": {
        "New York": ["New York", "Albany", "Buffalo"],
        "Massachusetts": ["Boston", "Worcester"],
        "Pennsylvania": ["Philadelphia", "Pittsburgh"],
        "New Jersey": ["Newark", "Jersey City"],
    },
    "Midwest": {
        "Illinois": ["Chicago", "Springfield"],
        "Ohio": ["Columbus", "Cleveland"],
        "Michigan": ["Detroit", "Grand Rapids"],
        "Minnesota": ["Minneapolis", "Saint Paul"],
    },
    "South": {
        "Texas": ["Houston", "Dallas", "Austin"],
        "Oklahoma": ["Oklahoma City", "Tulsa"],
        "Tennessee": ["Nashville", "Memphis"],
        "Louisiana": ["New Orleans", "Baton Rouge"],
    },
    "Southeast": {
        "Florida": ["Miami", "Orlando", "Tampa"],
        "Georgia": ["Atlanta", "Savannah"],
        "North Carolina": ["Charlotte", "Raleigh"],
        "Virginia": ["Richmond", "Virginia Beach"],
    },
    "West": {
        "California": ["Los Angeles", "San Francisco", "San Diego"],
        "Washington": ["Seattle", "Spokane"],
        "Colorado": ["Denver", "Colorado Springs"],
        "Nevada": ["Las Vegas", "Reno"],
    },
}

PRODUCTS = {
    "Men's Street Footwear": ("Footwear", 55, 110),
    "Men's Athletic Footwear": ("Footwear", 60, 130),
    "Women's Street Footwear": ("Footwear", 50, 105),
    "Women's Athletic Footwear": ("Footwear", 55, 120),
    "Men's Apparel": ("Apparel", 25, 70),
    "Women's Apparel": ("Apparel", 25, 65),
}

SALES_METHODS = ["In-store", "Outlet", "Online"]

# Channel-level behavior (this is the core "story" the analysis will surface)
CHANNEL_PROFILE = {
    # discount_rate: avg % taken off list price before margin
    # margin_rate: operating margin applied to net sales
    "In-store":  {"discount_mean": 0.06, "discount_sd": 0.03, "margin_mean": 0.44, "margin_sd": 0.05, "weight": 0.42},
    "Online":    {"discount_mean": 0.14, "discount_sd": 0.05, "margin_mean": 0.36, "margin_sd": 0.06, "weight": 0.33},
    "Outlet":    {"discount_mean": 0.28, "discount_sd": 0.06, "margin_mean": 0.27, "margin_sd": 0.06, "weight": 0.25},
}

# Regional discounting overlay (some regions discount harder -> margin drag)
REGION_DISCOUNT_ADJ = {
    "Northeast": 0.00,
    "Midwest": 0.01,
    "South": 0.03,
    "Southeast": 0.02,
    "West": -0.01,
}

START_DATE = date(2020, 1, 1)
END_DATE = date(2021, 12, 31)
N_ROWS = 9648


def random_dates(n):
    span = (END_DATE - START_DATE).days
    offsets = rng.integers(0, span + 1, size=n)
    return [START_DATE + timedelta(days=int(o)) for o in offsets]


def build():
    retailers = list(RETAILERS.keys())
    regions = list(REGION_STATES_CITIES.keys())
    products = list(PRODUCTS.keys())
    methods = list(CHANNEL_PROFILE.keys())
    method_weights = [CHANNEL_PROFILE[m]["weight"] for m in methods]

    rows = []
    dates = random_dates(N_ROWS)

    for i in range(N_ROWS):
        retailer = rng.choice(retailers)
        region = rng.choice(regions)
        state = rng.choice(list(REGION_STATES_CITIES[region].keys()))
        city = rng.choice(REGION_STATES_CITIES[region][state])
        product = rng.choice(products)
        cat, price_lo, price_hi = PRODUCTS[product]
        method = rng.choice(methods, p=method_weights)

        list_price = round(float(rng.uniform(price_lo, price_hi)), 2)

        # discounting: channel baseline + regional overlay + noise
        prof = CHANNEL_PROFILE[method]
        discount = rng.normal(prof["discount_mean"] + REGION_DISCOUNT_ADJ[region], prof["discount_sd"])
        discount = float(np.clip(discount, 0.0, 0.55))

        price_per_unit = round(list_price * (1 - discount), 2)
        units_sold = int(rng.integers(15, 850))
        total_sales = round(price_per_unit * units_sold, 2)

        margin = rng.normal(prof["margin_mean"] - 0.4 * discount * 0.5, prof["margin_sd"])
        margin = float(np.clip(margin, 0.05, 0.65))
        operating_profit = round(total_sales * margin, 2)
        operating_margin = round(margin, 4)

        rows.append({
            "Retailer": retailer,
            "Retailer ID": RETAILERS[retailer],
            "Invoice Date": dates[i].isoformat(),
            "Region": region,
            "State": state,
            "City": city,
            "Product": product,
            "Price per Unit": price_per_unit,
            "Units Sold": units_sold,
            "Total Sales": total_sales,
            "Operating Profit": operating_profit,
            "Operating Margin": operating_margin,
            "Sales Method": method,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Invoice Date").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = build()
    out_path = "data/adidas_us_sales.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df):,} rows to {out_path}")
    print(df.head())
    print("\nColumn dtypes:\n", df.dtypes)
