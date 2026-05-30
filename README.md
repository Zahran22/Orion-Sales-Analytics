# Orion-Technical-Assessment

# Project Overview

This project was developed as part of the Orion Technical Assessment for the Data Analytics Solutions Engineer role.
The objective is to transform raw sales and forecast JSON data into a structured analytical model, build a relational star schema, and create a Power BI dashboard that enables sales analysis, forecast comparison, and customer behavior insights.

ETL Logic
# 1. Data Extraction

The ETL process loads data from two JSON files:

Sales.json
forecast.json

using Python and Pandas.

# 2. Data Cleaning

The following data quality checks and transformations were applied:

Removed duplicate records
Trimmed leading and trailing spaces
Converted columns to appropriate data types
Standardized date formats
Removed invalid sales records
Handled null and inconsistent values
# 3. Data Transformation

The raw data was normalized into a relational star schema.

Dimensions
dim_product

Contains product-related attributes.

dim_customer

Contains customer-related attributes.

dim_geography

Contains continent, country, state, and city information.

dim_date

Contains calendar attributes used for time analysis.

Fact Tables
fact_sales

Stores transactional sales data at the order-line level.

fact_forecast

Stores forecasted sales values.

# 4. Keys and Relationships

Surrogate keys were generated for all dimensions:

ProductSRKey
CustomerSRKey
GeographySRKey
DateSRKey

Fact tables use these surrogate keys as foreign keys to support a proper relational design and improve reporting performance.

# Data Model

The solution follows a Star Schema architecture.

# Dimensions
dim_product
dim_customer
dim_geography
dim_date
# Facts
fact_sales
fact_forecast
# Relationships
Dimension	Fact Table
dim_product	fact_sales
dim_customer	fact_sales
dim_geography	fact_sales
dim_date	fact_sales
dim_product	fact_forecast
dim_geography	fact_forecast
dim_date	fact_forecast

# All relationships are configured as:

One-to-Many (1:*)
Single Direction
Active Relationships
Dashboard Requirements Implemented

<img width="503" height="314" alt="Data Model" src="https://github.com/user-attachments/assets/7e246a94-e2c3-47b7-8fbf-3e9bcb16714d" />


# The Power BI dashboard includes:

Total Sales Analysis

Analysis of total sales across different time granularities.

Sales Comparison (2008 vs 2009)

Comparison of sales performance between 2008 and 2009 using DAX measures.

Top 10 Products

Identification of top-performing products and their contribution to total sales.

Forecast vs Actual Analysis

Comparison between forecasted and actual sales performance.

Customer Behavior Analysis

Analysis of top customers and the products they purchase.

Geographic Filtering

<img width="592" height="329" alt="Dashboard" src="https://github.com/user-attachments/assets/1625b5c2-703a-467b-b731-11ac5e0e42f5" />

# Interactive filtering by:
Country
State

# Key KPIs

Total Sales
Sales 2008
Sales 2009
Sales Growth
Sales Growth %
Total Forecast
Forecast Variance
Forecast Accuracy %
Top Product Share %
Total Customers
Forecast Gap 
Actual vs Forecast %

# Key Assumptions
Sales data grain is at the transaction/order-line level.
Forecast data grain is Year × Country × Brand.
Forecast and Sales tables are connected through shared dimensions only.
Surrogate keys are used for all dimensions.
Duplicate records are removed during the transformation process.
Date dimension is used as the common calendar table for reporting and analysis.

# Repository Structure
Orion-Technical-Assessment/
│
├── etl.py
│
├── output/
│   ├── dim_product.csv
│   ├── dim_customer.csv
│   ├── dim_geography.csv
│   ├── dim_date.csv
│   ├── fact_sales.csv
│   └── fact_forecast.csv
│
├── data_model/
│   └── data_model.png
│
├── powerbi/
│   └── Orion_Dashboard.pbix
│
└── README.md

# Technologies Used
Python
Pandas
Power BI
DAX
Star Schema Modeling
