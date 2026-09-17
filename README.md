# E-commerce Analytics

A versioned analytics project built around the **Olist Brazilian E-Commerce dataset**, progressing from Excel analysis to interactive Power BI analytics and, later, an AI-powered analytics application.

## Current Version: v2.0 — Power BI Interactive Analytics

### What I built

Built an interactive Power BI dashboard to analyze e-commerce sales, order volume, customer geography, product categories, and delivery performance.

The dashboard includes:

- KPI cards for total orders, item sales, customers, and delivery variance
- Item sales analysis by product category
- Monthly order-volume trends
- Delivery variance analysis by Brazilian state
- Top-city analysis
- Date, state, product-category, and customer-city slicers
- Category → Product drill-down
- State → City drill-down
- Cross-filtering and interactive visual exploration
- An Insights & Analytics page with business observations
- A Data Dictionary page describing the model and metrics

### Key Findings

- **99,441 orders** are included in the analysis.
- Total item sales are approximately **R$13.59M**.
- **Health & Beauty** is the largest product category by item sales at approximately **R$1.26M**.
- The top 10 product categories account for approximately **62.4%** of total item sales.
- Average delivery variance is approximately **-11.2 days**, meaning delivered orders were earlier than their estimated delivery dates on average.
- **November 2017** recorded **7,544 orders**, representing approximately **62.9% MoM growth** from October 2017.

### Data Model

The Power BI model connects:

```text
Customers
    ↓
Orders
    ↓
Order Items
    ↓
Products
    ↓
Category Translation