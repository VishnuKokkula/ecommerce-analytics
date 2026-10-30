
from pathlib import Path

import pandas as pd
import streamlit as st
from openai import OpenAI, APIError, APIConnectionError, APIStatusError

# ============================================================
# Configuration
# ============================================================

APP_TITLE = "E-commerce Analytics (Olist Brazil)"
DATA_FILE = Path(__file__).resolve().parent / "metrics_summary.csv"

MODEL_NAME = "openai/gpt-oss-120b"
MAX_QUESTION_LENGTH = 1000
MAX_RESPONSE_TOKENS = 700


# ============================================================
# Page setup
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
)

st.title(APP_TITLE)
st.caption(
    "An analytical view of Brazilian e-commerce performance "
    "using aggregated Olist dataset metrics."
)


# ============================================================
# Actual CSV schema
# ============================================================

REQUIRED_COLUMNS = {
    "level",
    "dimension",
    "item_sales_brl",
    "order_count",
    "avg_delivery_variance_days",
}


def load_metrics():
    """Load the existing aggregated CSV without changing its schema."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"{DATA_FILE.name} was not found. "
            "Run build_metrics.py to generate it."
        )

    df = pd.read_csv(DATA_FILE)

    missing = REQUIRED_COLUMNS.difference(df.columns)

    if missing:
        raise ValueError(
            "The CSV is missing required columns: "
            + ", ".join(sorted(missing))
            + ". Expected columns: "
            + ", ".join(sorted(REQUIRED_COLUMNS))
        )

    if df.empty:
        raise ValueError("The metrics CSV contains no rows.")

    df["level"] = df["level"].fillna("").astype(str).str.strip().str.lower()
    df["dimension"] = df["dimension"].fillna("").astype(str).str.strip()

    for column in [
        "item_sales_brl",
        "order_count",
        "avg_delivery_variance_days",
    ]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def get_rows(df, level):
    """Return records for exactly one aggregation level."""
    return df[df["level"] == level].copy()


def format_brl(value):
    if pd.isna(value):
        return "N/A"
    return f"R${value:,.2f}"


def format_count(value):
    if pd.isna(value):
        return "N/A"
    return f"{int(value):,}"


def format_days(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:,.2f} days"


def clear_api_key():
    st.session_state["groq_api_key"] = ""
    st.session_state["api_key_input"] = ""
    st.session_state["ai_answer"] = ""
    st.session_state["ai_error"] = ""


def get_saved_api_key():
    """Read the Groq API key from Streamlit secrets, if configured."""
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if isinstance(key, str) and key.strip():
            return key.strip()
    except Exception:
        # A secrets file is optional; the user can enter a key below.
        pass

    return ""


def build_ai_context(df):
    """Send only the small, aggregated metrics file to the API."""
    columns = [
        "level",
        "dimension",
        "item_sales_brl",
        "order_count",
        "avg_delivery_variance_days",
    ]

    return df[columns].to_csv(index=False)


def extract_api_error(exc):
    """Extract the actual API error without exposing credentials."""
    status = getattr(exc, "status_code", "unknown")
    message = str(exc)
    request_id = None

    response = getattr(exc, "response", None)

    if response is not None:
        try:
            request_id = response.headers.get("x-request-id") or response.headers.get("request-id")
        except Exception:
            pass

        try:
            body = response.json()
            error = body.get("error", {})

            if isinstance(error, dict):
                message = error.get("message", message)
            elif error:
                message = str(error)

        except Exception:
            pass

    return status, message, request_id


# ============================================================
# Load metrics
# ============================================================

try:
    metrics_df = load_metrics()
except (OSError, ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
    st.error("The metrics file could not be loaded or validated.")
    st.code(str(exc))
    st.stop()


# ============================================================
# Split aggregation levels
# ============================================================

category_df = get_rows(metrics_df, "category")
state_df = get_rows(metrics_df, "state")
overall_df = get_rows(metrics_df, "overall")

# Do not silently treat an unknown level as an overall summary.
# The CSV's level field determines what each row represents.


# ============================================================
# Performance overview
# ============================================================

st.subheader("Performance overview")

if not overall_df.empty:
    # The overall row is the authoritative source for national totals.
    overall = overall_df.iloc[0]

    total_item_sales = overall["item_sales_brl"]
    total_orders = overall["order_count"]
    avg_delivery_variance = overall["avg_delivery_variance_days"]

else:
    # Category rows partition item sales, including untranslated items.
    # They do not provide a valid national order count when summed.
    total_item_sales = category_df["item_sales_brl"].sum(min_count=1)
    total_orders = None
    avg_delivery_variance = None

    st.warning(
        "No row with level='overall' was found. Item sales are shown as "
        "the sum of category-level sales, but national order count and "
        "national delivery variance are shown as unavailable. "
        "Check build_metrics.py if the overall row should exist."
    )

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Item Sales", format_brl(total_item_sales))

with kpi2:
    st.metric(
        "Distinct Orders",
        format_count(total_orders) if total_orders is not None else "N/A",
    )

with kpi3:
    category_count = category_df["dimension"].nunique()
    st.metric("Product Categories", format_count(category_count))

with kpi4:
    st.metric("Avg. Delivery Variance", format_days(avg_delivery_variance))

st.caption(
    "Item Sales is the sum of order-item prices and excludes freight. "
    "Delivery variance = actual delivery date − estimated delivery date. "
    "Negative means earlier than estimated; positive means later."
)


# ============================================================
# Category performance
# ============================================================

st.divider()
st.subheader("Category performance")

if category_df.empty:
    st.info("No category-level records are available.")

else:
    category_table = (
        category_df[
            ["dimension", "item_sales_brl", "order_count"]
        ]
        .sort_values("item_sales_brl", ascending=False, na_position="last")
        .rename(
            columns={
                "dimension": "Product Category",
                "item_sales_brl": "Item Sales (R$)",
                "order_count": "Orders",
            }
        )
        .reset_index(drop=True)
    )

    category_table["Item Sales (R$)"] = category_table[
        "Item Sales (R$)"
    ].round(2)

    category_table["Orders"] = category_table["Orders"].astype("Int64")

    st.caption(
        "Categories are ranked by item sales. An order can contain products "
        "from more than one category, so category order counts are not additive."
    )

    st.dataframe(
        category_table,
        width="stretch",
        hide_index=True,
    )

    top_categories = (
        category_df.sort_values(
            "item_sales_brl",
            ascending=False,
            na_position="last",
        )
        .head(10)
        .sort_values("item_sales_brl", ascending=True)
    )

    if not top_categories.empty:
        chart_data = top_categories.set_index("dimension")[
            ["item_sales_brl"]
        ]

        st.markdown("**Top 10 categories by item sales**")

        st.bar_chart(
            chart_data,
            x_label="Product category",
            y_label="Item sales (R$)",
        )


# ============================================================
# Customer-state performance
# ============================================================

st.divider()
st.subheader("Customer-state performance")

if state_df.empty:
    st.info("No state-level records are available.")

else:
    state_table = (
        state_df[
            [
                "dimension",
                "item_sales_brl",
                "order_count",
                "avg_delivery_variance_days",
            ]
        ]
        .sort_values("item_sales_brl", ascending=False, na_position="last")
        .rename(
            columns={
                "dimension": "Customer State",
                "item_sales_brl": "Item Sales (R$)",
                "order_count": "Orders",
                "avg_delivery_variance_days": "Avg. Delivery Variance (days)",
            }
        )
        .reset_index(drop=True)
    )

    state_table["Item Sales (R$)"] = state_table["Item Sales (R$)"].round(2)
    state_table["Orders"] = state_table["Orders"].astype("Int64")
    state_table["Avg. Delivery Variance (days)"] = state_table[
        "Avg. Delivery Variance (days)"
    ].round(2)

    st.caption(
        "State-level metrics describe customer states. Do not add state-level "
        "delivery averages to derive a national average."
    )

    st.dataframe(
        state_table,
        width="stretch",
        hide_index=True,
    )

    top_states = (
        state_df.sort_values(
            "item_sales_brl",
            ascending=False,
            na_position="last",
        )
        .head(10)
        .sort_values("item_sales_brl", ascending=True)
    )

    if not top_states.empty:
        chart_data = top_states.set_index("dimension")[["item_sales_brl"]]

        st.markdown("**Top 10 states by item sales**")

        st.bar_chart(
            chart_data,
            x_label="Customer state",
            y_label="Item sales (R$)",
        )


# ============================================================
# Initial observations
# ============================================================

st.divider()
st.subheader("Initial observations")

if not category_df.empty:
    top_category = category_df.loc[category_df["item_sales_brl"].idxmax()]

    st.write(
        f"- Highest item-sales category: **{top_category['dimension']}** "
        f"({format_brl(top_category['item_sales_brl'])})."
    )

if not state_df.empty:
    top_state = state_df.loc[state_df["item_sales_brl"].idxmax()]

    st.write(
        f"- Highest item-sales customer state: **{top_state['dimension']}** "
        f"({format_brl(top_state['item_sales_brl'])})."
    )

if pd.notna(avg_delivery_variance):
    if avg_delivery_variance < 0:
        st.write(
            f"- Average delivery variance is {abs(avg_delivery_variance):.2f} "
            "days earlier than estimated."
        )
    elif avg_delivery_variance > 0:
        st.write(
            f"- Average delivery variance is {avg_delivery_variance:.2f} "
            "days later than estimated."
        )
    else:
        st.write("- Average delivery variance is zero days.")

with st.expander("Metric definitions and limitations"):
    st.markdown(
        """
        **Definitions**

        - **Item Sales:** sum of order-item prices (`price`); freight excluded.
        - **Orders:** distinct order IDs, not the number of order-item rows.
        - **Delivery variance:** actual customer delivery date minus the
          estimated delivery date, in days.
        - Negative delivery variance means early delivery; positive means
          late delivery.

        **Limitations**

        - These are descriptive metrics, not evidence of causation.
        - Item sales are not profit and do not include freight.
        - Category and state rows are separate views of the same business.
        - Category or state order counts should not be summed to calculate
          national distinct orders.
        - An overall delivery average should not be calculated as a simple
          average of state averages.
        - Orders without usable delivery dates cannot contribute to the
          delivery-variance average.
        - `Unknown / untranslated` is retained as a category rather than
          silently discarded.
        """
    )


# ============================================================
# AI question answering — Groq
# ============================================================

st.divider()
st.subheader("Ask questions about the data")

st.write(
    "Ask questions about the available aggregated category, state, sales, "
    "order, and delivery metrics."
)

st.info(
    "The AI feature sends your question and the aggregated metrics CSV "
    "to Groq. It does not send the raw order or customer CSV files."
)

if "groq_api_key" not in st.session_state:
    st.session_state["groq_api_key"] = get_saved_api_key()

if "ai_answer" not in st.session_state:
    st.session_state["ai_answer"] = ""

if "ai_error" not in st.session_state:
    st.session_state["ai_error"] = ""

with st.form("api_key_form"):
    st.text_input(
        "Groq API key (optional if configured in secrets.toml)",
        type="password",
        key="api_key_input",
        placeholder="Paste your Groq API key if needed",
        help=(
            "Alternatively, configure GROQ_API_KEY in "
            ".streamlit/secrets.toml."
        ),
    )

    use_key = st.form_submit_button("Use this API key")

if use_key:
    supplied_key = st.session_state.get("api_key_input", "").strip()

    if supplied_key:
        st.session_state["groq_api_key"] = supplied_key
        st.session_state["ai_answer"] = ""
        st.session_state["ai_error"] = ""
        st.success("Groq API key set for this Streamlit session.")
    else:
        st.session_state["ai_error"] = (
            "Enter a Groq API key, or configure GROQ_API_KEY "
            "in .streamlit/secrets.toml."
        )

st.button("Forget API key", on_click=clear_api_key)

with st.form("question_form"):
    question = st.text_area(
        "Your question",
        placeholder=(
            "Which five product categories have the highest item sales?"
        ),
        max_chars=MAX_QUESTION_LENGTH,
        height=100,
    )

    ask_clicked = st.form_submit_button("Generate answer")

if ask_clicked:
    api_key = st.session_state.get("groq_api_key", "").strip()

    if not api_key:
        st.session_state["ai_error"] = (
            "No Groq API key is configured. Enter one above or configure "
            "GROQ_API_KEY in .streamlit/secrets.toml."
        )
        st.session_state["ai_answer"] = ""

    elif not question.strip():
        st.session_state["ai_error"] = "Enter a question first."
        st.session_state["ai_answer"] = ""

    else:
        system_prompt = """
You are a careful data analyst answering questions about the Olist Brazil
e-commerce dataset.

Use only the aggregated CSV provided in the user message. Do not invent
numbers, categories, states, dates, or findings.

The CSV schema is:
- level: category, state, or overall
- dimension: category name, state code, or overall label
- item_sales_brl: item sales in Brazilian reais
- order_count: distinct order count at that aggregation level
- avg_delivery_variance_days: average delivery variance in days

Definitions:
- Item sales are the sum of order-item prices and exclude freight.
- Item sales are not profit and should not be described as profit.
- Delivery variance = actual delivery date minus estimated delivery date.
- Negative means early delivery; positive means late delivery.

Rules:
- Use the overall row for national totals when present.
- Do not add category order counts to calculate national orders.
- Do not add state order counts to calculate national orders.
- Category and state sales rows are alternative views of the same sales,
  so never add them together.
- Do not average state delivery averages to calculate a national average.
- If the required metric is missing, explicitly say it is unavailable.
- Do not infer customer age, profit, marketing spend, customer satisfaction,
  causation, or revenue at risk unless the supplied data supports it.
- Keep the answer concise and distinguish facts from interpretation.
"""

        user_message = (
            "AGGREGATED METRICS CSV:\n\n"
            + build_ai_context(metrics_df)
            + "\nQUESTION:\n"
            + question.strip()
        )

        try:
            with st.spinner("Analyzing the available metrics with Groq..."):
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1",
                    timeout=45.0,
                    max_retries=0,
                )

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    max_completion_tokens=MAX_RESPONSE_TOKENS,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                )

            answer = (response.choices[0].message.content or "").strip()

            if answer:
                st.session_state["ai_answer"] = answer
                st.session_state["ai_error"] = ""
            else:
                st.session_state["ai_answer"] = ""
                st.session_state["ai_error"] = "Groq returned no readable text."

        except APIStatusError as exc:
            status, message, request_id = extract_api_error(exc)
            error_details = f"HTTP status: {status}\nGroq error: {message}"

            if request_id:
                error_details += f"\nRequest ID: {request_id}"

            st.session_state["ai_answer"] = ""
            st.session_state["ai_error"] = error_details

        except APIConnectionError:
            st.session_state["ai_answer"] = ""
            st.session_state["ai_error"] = (
                "Could not connect to Groq. Check your internet connection "
                "and try again."
            )

        except APIError as exc:
            st.session_state["ai_answer"] = ""
            st.session_state["ai_error"] = (
                f"Groq SDK error ({type(exc).__name__}): {exc}"
            )

        except Exception as exc:
            st.session_state["ai_answer"] = ""
            st.session_state["ai_error"] = (
                f"Unexpected error ({type(exc).__name__}): {exc}"
            )

if st.session_state.get("ai_error"):
    st.error("The AI request failed.")
    st.code(st.session_state["ai_error"])

if st.session_state.get("ai_answer"):
    st.markdown("### Answer")
    st.markdown(st.session_state["ai_answer"])


# ============================================================
# Footer
# ============================================================

st.divider()
st.caption(
    "Built with Python, pandas, Streamlit, and the Groq API."
)
