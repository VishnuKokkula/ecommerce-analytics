from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).resolve().parent / "metrics_summary.csv"

REQUIRED_COLUMNS = [
    "level",
    "dimension",
    "item_sales_brl",
    "order_count",
    "avg_delivery_variance_days",
]


def load_metrics() -> pd.DataFrame:
    """Load and validate the existing aggregated metrics CSV."""
    df = pd.read_csv(DATA_FILE)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if df["level"].isna().any() or df["dimension"].isna().any():
        raise ValueError("Metrics contain missing level or dimension values.")

    for column in [
        "item_sales_brl",
        "order_count",
        "avg_delivery_variance_days",
    ]:
        df[column] = pd.to_numeric(df[column], errors="raise")

    if not df["level"].isin(["category", "state", "overall"]).all():
        raise ValueError("Unexpected aggregation level in metrics CSV.")

    if df.duplicated(["level", "dimension"]).any():
        raise ValueError("Duplicate level/dimension rows found.")

    return df


def top_categories(limit: int = 5) -> list[dict]:
    """Return categories ranked by item sales, calculated in pandas."""
    if limit < 1:
        raise ValueError("limit must be at least 1.")

    df = load_metrics()
    categories = df.loc[df["level"].eq("category")].copy()

    if categories.empty:
        raise ValueError("No category metrics are available.")

    categories = categories.sort_values(
        ["item_sales_brl", "dimension"],
        ascending=[False, True],
    ).head(limit)

    return [
        {
            "rank": rank,
            "category": row["dimension"],
            "item_sales_brl": round(float(row["item_sales_brl"]), 2),
            "order_count": int(row["order_count"]),
        }
        for rank, (_, row) in enumerate(categories.iterrows(), start=1)
    ]


def overall_metrics() -> dict:
    """Return verified overall metrics without replacing missing values."""
    df = load_metrics()
    overall = df.loc[df["level"].eq("overall")]

    if len(overall) != 1:
        raise ValueError(
            f"Expected exactly one overall row; found {len(overall)}."
        )

    row = overall.iloc[0]
    variance = row["avg_delivery_variance_days"]

    return {
        "item_sales_brl": round(float(row["item_sales_brl"]), 2),
        "order_count": int(row["order_count"]),
        "avg_delivery_variance_days": (
            None if pd.isna(variance) else round(float(variance), 2)
        ),
    }


def sales_difference_between_top_and_bottom(limit: int = 5) -> float:
    """Calculate the sales difference between first and last of the top N."""
    ranked = top_categories(limit)

    if len(ranked) < 2:
        raise ValueError("At least two categories are needed.")

    return round(
        ranked[0]["item_sales_brl"] - ranked[-1]["item_sales_brl"],
        2,
    )
