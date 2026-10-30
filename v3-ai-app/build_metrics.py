
from pathlib import Path
import pandas as pd

# Paths
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "v1-excel" / "raw-data"
OUTPUT = Path(__file__).resolve().parent / "metrics_summary.csv"

# Load only the columns required for the analysis
orders = pd.read_csv(
    DATA / "olist_orders_dataset.csv",
    usecols=[
        "order_id",
        "customer_id",
        "order_status",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
)

items = pd.read_csv(
    DATA / "olist_order_items_dataset.csv",
    usecols=["order_id", "product_id", "price"],
)

products = pd.read_csv(
    DATA / "olist_products_dataset.csv",
    usecols=["product_id", "product_category_name"],
)

customers = pd.read_csv(
    DATA / "olist_customers_dataset.csv",
    usecols=["customer_id", "customer_state"],
)

translations = pd.read_csv(
    DATA / "product_category_name_translation.csv"
)

# Translate categories while retaining untranslated/missing categories
products = products.merge(
    translations,
    on="product_category_name",
    how="left",
)

products["category"] = (
    products["product_category_name_english"]
    .fillna(products["product_category_name"])
    .fillna("Unknown / untranslated")
)

# Parse delivery dates
for column in [
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

# One row per order for delivery calculations
valid_delivery = orders[
    orders["order_delivered_customer_date"].notna()
    & orders["order_estimated_delivery_date"].notna()
].copy()

valid_delivery["delivery_variance_days"] = (
    valid_delivery["order_delivered_customer_date"]
    - valid_delivery["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

# Item-level sales: price only; freight is excluded
item_data = items.merge(products[["product_id", "category"]], on="product_id", how="left")
item_data["category"] = item_data["category"].fillna("Unknown / untranslated")

category_metrics = (
    item_data.groupby("category", dropna=False)
    .agg(
        item_sales_brl=("price", "sum"),
        order_count=("order_id", "nunique"),
    )
    .reset_index()
    .rename(columns={"category": "dimension"})
)

category_metrics["level"] = "category"
category_metrics["avg_delivery_variance_days"] = pd.NA

# Attribute item sales to the customer's state
state_items = (
    items.merge(orders[["order_id", "customer_id"]], on="order_id", how="left")
    .merge(customers, on="customer_id", how="left")
)

state_items["customer_state"] = state_items["customer_state"].fillna("Unknown")

state_sales = (
    state_items.groupby("customer_state")
    .agg(
        item_sales_brl=("price", "sum"),
        order_count=("order_id", "nunique"),
    )
    .reset_index()
    .rename(columns={"customer_state": "dimension"})
)

# Delivery variance is calculated once per order, not once per item
state_delivery = (
    valid_delivery.merge(
        customers[["customer_id", "customer_state"]],
        on="customer_id",
        how="left",
    )
    .assign(customer_state=lambda df: df["customer_state"].fillna("Unknown"))
    .groupby("customer_state")["delivery_variance_days"]
    .mean()
    .reset_index()
    .rename(
        columns={
            "customer_state": "dimension",
            "delivery_variance_days": "avg_delivery_variance_days",
        }
    )
)

state_metrics = state_sales.merge(state_delivery, on="dimension", how="left")
state_metrics["level"] = "state"

# Keep a consistent schema
columns = [
    "level",
    "dimension",
    "item_sales_brl",
    "order_count",
    "avg_delivery_variance_days",
]

summary = pd.concat(
    [
        category_metrics[columns],
        state_metrics[columns],
    ],
    ignore_index=True,
)

summary["item_sales_brl"] = summary["item_sales_brl"].round(2)
summary["avg_delivery_variance_days"] = (
    pd.to_numeric(summary["avg_delivery_variance_days"], errors="coerce").round(2)
)
# Overall metrics use the complete source tables
overall_row = pd.DataFrame([{
    "level": "overall",
    "dimension": "All orders",
    "item_sales_brl": round(items["price"].sum(), 2),
    "order_count": int(orders["order_id"].nunique()),
    "avg_delivery_variance_days": round(
        valid_delivery["delivery_variance_days"].mean(), 2
    ),
}])

summary = pd.concat([summary, overall_row], ignore_index=True)
summary.to_csv(OUTPUT, index=False)

# Validation output — do not assume these match until checked
print(f"Saved: {OUTPUT}")
print(f"Summary rows: {len(summary)}")
print(f"Category rows: {(summary['level'] == 'category').sum()}")
print(f"State rows: {(summary['level'] == 'state').sum()}")
print(f"Item sales total: R${items['price'].sum():,.2f}")
print(f"Distinct orders in source: {orders['order_id'].nunique():,}")
print(f"Orders with usable delivery dates: {len(valid_delivery):,}")
print("\nTop 5 categories by item sales:")
print(
    category_metrics.nlargest(5, "item_sales_brl")[
        ["dimension", "item_sales_brl", "order_count"]
    ].to_string(index=False)
)
