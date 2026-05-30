
"""
Orion Technical Assessment – Enhanced ETL Pipeline
==================================================
Enhancements:
-------------
1. Remove duplicated rows from all tables.
2. Add surrogate keys (SRKeys) to all dimensions.
3. Use surrogate keys as foreign keys inside fact tables.
4. Normalize forecast table with dimension references.
5. Proper Star Schema design.
"""

import json
import os
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = BASE_DIR
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

SALES_PATH = os.path.join(ROOT_DIR, "Sales.json")
FORECAST_PATH = os.path.join(ROOT_DIR, "forecast.json")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def log(msg: str):
    print(f"[ETL] {msg}")


def save(df: pd.DataFrame, file_name: str):
    path = os.path.join(OUTPUT_DIR, file_name)
    df.to_csv(path, index=False)
    log(f"Saved -> {file_name} | Rows: {len(df)} | Cols: {len(df.columns)}")


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
log("Loading Sales.json ...")

raw_sales = json.load(open(SALES_PATH, encoding="utf-8"))
df = pd.DataFrame(raw_sales)

log(f"Sales Records Loaded: {len(df):,}")

log("Loading forecast.json ...")

raw_forecast = json.load(open(FORECAST_PATH, encoding="utf-8"))
df_fc = pd.DataFrame(raw_forecast)

log(f"Forecast Records Loaded: {len(df_fc):,}")


# ─────────────────────────────────────────────────────────────────────────────
# CLEANING & STANDARDIZATION
# ─────────────────────────────────────────────────────────────────────────────
log("Cleaning data ...")

# Remove duplicated rows
before_sales = len(df)
df = df.drop_duplicates()

log(f"Removed {before_sales - len(df):,} duplicated rows from Sales")

before_forecast = len(df_fc)
df_fc = df_fc.drop_duplicates()

log(f"Removed {before_forecast - len(df_fc):,} duplicated rows from Forecast")

# Trim whitespace
str_cols = df.select_dtypes(include="object").columns

for col in str_cols:
    df[col] = df[col].astype(str).str.strip()

str_cols_fc = df_fc.select_dtypes(include="object").columns

for col in str_cols_fc:
    df_fc[col] = df_fc[col].astype(str).str.strip()

# Convert dates
df["OrderDate"] = pd.to_datetime(
    df["OrderDate"],
    format="%m/%d/%Y",
    errors="coerce"
)

# Numeric conversions
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["Net Price"] = pd.to_numeric(df["Net Price"], errors="coerce")

# Remove invalid rows
before = len(df)

df = df[
    df["Quantity"].notna() &
    df["Net Price"].notna() &
    (df["Quantity"] > 0)
].copy()

log(f"Removed {before - len(df):,} invalid rows")

# Derived measure
df["SalesAmount"] = df["Quantity"] * df["Net Price"]


# ─────────────────────────────────────────────────────────────────────────────
# DIM_PRODUCT
# ─────────────────────────────────────────────────────────────────────────────
log("Building dim_product ...")

product_cols = [
    "ProductKey",
    "Product Name",
    "Brand",
    "Color",
    "Subcategory",
    "Category"
]

dim_product = (
    df[product_cols]
    .drop_duplicates(subset=["ProductKey"])
    .sort_values("ProductKey")
    .reset_index(drop=True)
)

# Add Surrogate Key
dim_product.insert(0, "ProductSRKey", range(1, len(dim_product) + 1))

# Rename columns
dim_product = dim_product.rename(columns={
    "Product Name": "ProductName",
    "Color": "ColorRaw"
})

save(dim_product, "dim_product.csv")


# ─────────────────────────────────────────────────────────────────────────────
# DIM_CUSTOMER
# ─────────────────────────────────────────────────────────────────────────────
log("Building dim_customer ...")

customer_cols = [
    "CustomerKey",
    "Customer Code",
    "Name",
    "Education",
    "Occupation"
]

dim_customer = (
    df[customer_cols]
    .sort_values(["CustomerKey", "Name"], na_position="last")
    .drop_duplicates(subset=["CustomerKey"])
    .reset_index(drop=True)
)

# Add Surrogate Key
dim_customer.insert(0, "CustomerSRKey", range(1, len(dim_customer) + 1))

dim_customer = dim_customer.rename(columns={
    "Customer Code": "CustomerCode"
})

save(dim_customer, "dim_customer.csv")


# ─────────────────────────────────────────────────────────────────────────────
# DIM_GEOGRAPHY
# ─────────────────────────────────────────────────────────────────────────────
log("Building dim_geography ...")

geo_cols = [
    "Continent",
    "CountryRegion",
    "State",
    "City"
]

dim_geography = (
    df[geo_cols]
    .drop_duplicates()
    .sort_values(geo_cols)
    .reset_index(drop=True)
)

# Add Surrogate Key
dim_geography.insert(
    0,
    "GeographySRKey",
    range(1, len(dim_geography) + 1)
)

save(dim_geography, "dim_geography.csv")


# ─────────────────────────────────────────────────────────────────────────────
# DIM_DATE
# ─────────────────────────────────────────────────────────────────────────────
log("Building dim_date ...")

start_date = df["OrderDate"].min()
end_date = df["OrderDate"].max()

date_range = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D"
)

dim_date = pd.DataFrame({
    "Date": date_range
})

# Add Surrogate Key
dim_date.insert(0, "DateSRKey", range(1, len(dim_date) + 1))

# Date attributes
dim_date["DateKey"] = dim_date["Date"].dt.strftime("%Y%m%d").astype(int)
dim_date["Year"] = dim_date["Date"].dt.year
dim_date["Quarter"] = dim_date["Date"].dt.quarter
dim_date["Month"] = dim_date["Date"].dt.month
dim_date["MonthName"] = dim_date["Date"].dt.strftime("%B")
dim_date["WeekOfYear"] = dim_date["Date"].dt.isocalendar().week.astype(int)
dim_date["Day"] = dim_date["Date"].dt.day
dim_date["DayName"] = dim_date["Date"].dt.strftime("%A")
dim_date["YearMonth"] = dim_date["Date"].dt.strftime("%Y-%m")

save(dim_date, "dim_date.csv")


# ─────────────────────────────────────────────────────────────────────────────
# ADD FOREIGN KEYS TO FACT SALES
# ─────────────────────────────────────────────────────────────────────────────
log("Building fact_sales ...")

# Add ProductSRKey
fact_sales = df.merge(
    dim_product[["ProductSRKey", "ProductKey"]],
    on="ProductKey",
    how="left"
)

# Add CustomerSRKey
fact_sales = fact_sales.merge(
    dim_customer[["CustomerSRKey", "CustomerKey"]],
    on="CustomerKey",
    how="left"
)

# Add GeographySRKey
fact_sales = fact_sales.merge(
    dim_geography,
    on=geo_cols,
    how="left"
)

# Add DateSRKey
fact_sales["DateKey"] = (
    fact_sales["OrderDate"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

fact_sales = fact_sales.merge(
    dim_date[["DateSRKey", "DateKey"]],
    on="DateKey",
    how="left"
)

# Keep only fact columns
fact_sales = fact_sales[[
    "DateSRKey",
    "ProductSRKey",
    "CustomerSRKey",
    "GeographySRKey",
    "Quantity",
    "Net Price",
    "SalesAmount"
]].copy()

# Add Fact Surrogate Key
fact_sales.insert(
    0,
    "SalesSRKey",
    range(1, len(fact_sales) + 1)
)

# Remove duplicates
fact_sales = fact_sales.drop_duplicates()

save(fact_sales, "fact_sales.csv")


# ─────────────────────────────────────────────────────────────────────────────
# FACT_FORECAST
# ─────────────────────────────────────────────────────────────────────────────
log("Building fact_forecast ...")

# Clean columns
df_fc.columns = [c.strip() for c in df_fc.columns]

# Convert Forecast
df_fc["Forecast"] = pd.to_numeric(
    df_fc["Forecast"],
    errors="coerce"
)

# Add ProductSRKey using Brand
forecast_df = df_fc.merge(
    dim_product[["ProductSRKey", "Brand"]].drop_duplicates(),
    on="Brand",
    how="left"
)

# Add GeographySRKey using CountryRegion
geo_country = dim_geography[
    ["GeographySRKey", "CountryRegion"]
].drop_duplicates()

forecast_df = forecast_df.merge(
    geo_country,
    on="CountryRegion",
    how="left"
)

# Create DateKey from Year
forecast_df["DateKey"] = (
    forecast_df["Year"].astype(str) + "0101"
).astype(int)

# Add DateSRKey
forecast_df = forecast_df.merge(
    dim_date[["DateSRKey", "DateKey"]],
    on="DateKey",
    how="left"
)

# Final Fact Forecast
fact_forecast = forecast_df[[
    "DateSRKey",
    "ProductSRKey",
    "GeographySRKey",
    "Forecast"
]].copy()

# Add Surrogate Key
fact_forecast.insert(
    0,
    "ForecastSRKey",
    range(1, len(fact_forecast) + 1)
)

# Rename column
fact_forecast = fact_forecast.rename(columns={
    "Forecast": "ForecastAmount"
})

# Remove duplicates
fact_forecast = fact_forecast.drop_duplicates()

save(fact_forecast, "fact_forecast.csv")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
log("=" * 60)
log("ETL COMPLETED SUCCESSFULLY")
log("=" * 60)

log(f"dim_product     : {len(dim_product):,} rows")
log(f"dim_customer    : {len(dim_customer):,} rows")
log(f"dim_geography   : {len(dim_geography):,} rows")
log(f"dim_date        : {len(dim_date):,} rows")
log(f"fact_sales      : {len(fact_sales):,} rows")
log(f"fact_forecast   : {len(fact_forecast):,} rows")

log(
    f"Total Sales Amount: "
    f"${fact_sales['SalesAmount'].sum():,.2f}"
)

