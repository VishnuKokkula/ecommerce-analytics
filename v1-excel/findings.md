# V1 Findings - Olist E-commerce Analytics

## Business Question

What do the Olist order, product, customer, and delivery data reveal about category sales concentration, delivery performance, and order-volume trends?

## Analysis Scope

The analysis uses the Olist Brazilian e-commerce dataset and focuses on:

- Item-level sales by translated product category
- Average delivery variance by customer state
- Monthly order volume and month-over-month growth

Item sales are calculated as the sum of `price` from the order-items data. Delivery variance is calculated as actual customer delivery date minus estimated delivery date. Negative values indicate delivery earlier than the estimated date.

Orders without usable delivery dates are excluded from the delivery-variance average but remain in the overall order dataset.

## Key Findings

### 1. Item sales are concentrated in a small group of categories

The top 10 product categories generated **R$8,475,957.56**, representing approximately **62.4%** of total item sales of **R$13,591,643.70**.

This indicates that a relatively small group of categories accounts for a large share of item-level sales activity.

### 2. Health & Beauty is the largest individual category

**Health & Beauty** generated **R$1,258,681.34** in item sales, making it the highest-selling product category in the analysis.

The next highest categories were **Watches & Gifts at R$1,205,005.68** and **Bed & Bath Table at R$1,036,988.68**.

### 3. Delivered orders arrived earlier than estimated on average

The overall average delivery variance was **-11.2 days** among orders with valid delivery and estimated delivery dates.

The state-level range was substantial: **AC averaged -20.1 days**, while **AL averaged -8.0 days**.

These values indicate that delivered orders were generally completed before the estimated delivery date, but the difference between states shows meaningful variation in delivery timing.

### 4. Order volume accelerated sharply in late 2017

November 2017 recorded the highest monthly order volume in the main analysis period, with **7,544 orders**, representing **62.9% month-over-month growth** from October 2017.

Order volume then declined to **5,673 orders in December 2017**, a **24.8% month-over-month decrease**, showing significant month-to-month volatility during this period.

### 5. Category translation remains a data-quality limitation

**1,627 order-item rows** had no translated product category and accounted for **R$185,049.76** in item sales, approximately **1.4% of total item sales**.

These records were retained rather than removed so that the analysis did not silently exclude their sales value.

## Recommendation

Prioritize inventory and operational monitoring for the **top 10 product categories**, which account for approximately **62.4% of item sales**, and use the **November 2017 demand spike of 7,544 orders and +62.9% MoM growth** as a benchmark when planning capacity for high-demand periods.

## Limitations

This analysis is descriptive rather than causal. Average delivery variance does not by itself measure logistics quality, customer satisfaction, or profitability. The September-October 2018 order counts are unusually low and were excluded from the main monthly trend chart because they appear to represent incomplete tail periods. The analysis also does not include seller performance, freight cost, payment behavior, or customer-review data.
