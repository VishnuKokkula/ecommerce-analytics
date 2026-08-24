# \# E-commerce Analytics

# 

# A versioned analytics project built around the \*\*Olist Brazilian E-Commerce dataset\*\*, progressing from Excel analysis to Power BI and an AI-powered application.

# 

# \## Current Version: v1.0 — Excel Static Analysis

# 

# \### What I built

# 

# Used \*\*Excel Power Query, PivotTables, and charts\*\* to analyze:

# 

# \* Product-category item sales

# \* Delivery variance by customer state

# \* Monthly order volume and MoM growth

# \* Data-quality issues in product-category translation

# 

# \### Key Findings

# 

# \* Top 10 product categories generated \*\*R$8.48M\*\*, approximately \*\*62.4%\*\* of total item sales.

# \* \*\*Health \& Beauty\*\* was the highest-selling category at \*\*R$1.26M\*\* in item sales.

# \* Average delivery variance was \*\*-11.2 days\*\*, meaning delivered orders were earlier than estimated on average.

# \* \*\*AC\*\* had the most negative average delivery variance at \*\*-20.1 days\*\*, versus \*\*-8.0 days\*\* in AL.

# \* \*\*November 2017\*\* recorded \*\*7,544 orders\*\*, with \*\*62.9% MoM growth\*\*.

# \* \*\*1,627 order-item rows\*\* lacked translated product categories, representing \*\*R$185K\*\* in item sales.

# 

# \### Data Approach

# 

# The analysis uses Power Query to transform and combine:

# 

# `Orders → Customers`

# 

# for order-level delivery and volume analysis, and:

# 

# `Order Items → Products → Category Translation`

# 

# for item-level category analysis.

# 

# The analysis deliberately keeps these grains separate to avoid over-weighting multi-item orders in delivery metrics.

# 

# Raw CSV data is stored locally and excluded from Git.

# 

# \### Deliverables

# 

# \*\*V1.0\*\*

# 

# \* \[Excel Analysis Workbook](v1-excel/track-a-v1-analysis.xlsx)

# \* \[Findings](v1-excel/findings.md)

# \* \[Analysis Screenshot](v1-excel/screenshot-v1.png)

# 

# \### Project Roadmap

# 

# | Version  | Focus                            | Status     |

# | -------- | -------------------------------- | ---------- |

# | \*\*v1.0\*\* | Excel static analysis            | ✅ Complete |

# | \*\*v2.0\*\* | Power BI interactive analytics   | Planned    |

# | \*\*v3.0\*\* | AI-powered analytics application | Planned    |

# 

# \### Tools

# 

# \*\*Excel · Power Query · PivotTables · Git · GitHub\*\*

# 

# \### Dataset

# 

# Olist Brazilian E-Commerce Public Dataset

# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce



