# E-commerce Analytics — Olist Brazil

An end-to-end analytics project exploring Brazilian e-commerce data using Excel, Power BI, Python, and a Streamlit application with AI-assisted explanations.

## Project Overview

This project analyzes the Olist Brazilian E-Commerce Public Dataset, progressing through three versions:

- **V1 — Excel Analytics:** Data exploration and analysis using Excel and Power Query.
- **V2 — Power BI Analytics:** Interactive dashboards for exploring sales, orders, product categories, geography, and delivery performance.
- **V3 — AI-Assisted Analytics:** A Streamlit application that calculates supported metrics in Python and uses Groq to explain verified results in natural language.

The goal is to demonstrate a practical workflow connecting data preparation, business intelligence, deterministic calculations, and an AI-assisted interface.

## Repository Structure

```text
ecommerce-analytics/
├── v1-excel/
│   ├── findings.md
│   ├── screenshot-v1.png
│   └── track-a-v1-analysis.xlsx
├── v2-powerbi/
│   ├── notes.md
│   ├── screenshot-v2.png
│   └── track-a-v2-dashboard.png
├── v3-ai-app/
│   ├── app.py
│   ├── analytics.py
│   ├── build_metrics.py
│   ├── metrics_summary.csv
│   ├── requirements.txt
│   └── .streamlit/
│       └── secrets.toml.example
├── .gitignore
└── README.md
```

The repository may contain additional supporting files. The local virtual environment, API secrets, Python cache, and temporary backups are excluded from version control.

## Dataset

**Brazilian E-Commerce Public Dataset by Olist**

Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

The dataset contains records related to Brazilian e-commerce orders, items, products, customers, sellers, payments, reviews, and delivery.

Refer to the original dataset page for its license and usage terms.

## V1 — Excel Analytics

The first version uses Excel and Power Query to prepare and analyze the dataset.

Included artifacts:

- Excel analysis workbook
- Findings document
- Screenshot of the analysis

See [`v1-excel/findings.md`](v1-excel/findings.md).

## V2 — Power BI Analytics

The second version explores the data through an interactive Power BI dashboard.

The documented dashboard features include:

- KPI cards for orders, item sales, customers, and delivery variance
- Item sales by product category
- Monthly order-volume trends
- Delivery variance by Brazilian state
- Top-city analysis
- Date, state, product-category, and customer-city slicers
- Category-to-product and state-to-city drill-down
- Cross-filtering and interactive exploration
- An insights page and data dictionary

Screenshots and project notes are available in [`v2-powerbi/`](v2-powerbi/).

The repository currently includes dashboard screenshots and notes; an editable Power BI `.pbix` file is not listed among the included artifacts.

## V3 — AI-Assisted Analytics

The third version uses Python for supported metric calculations and Streamlit for the user interface. Groq provides natural-language explanations for supported analytical results.

Key files:

- `app.py` — Streamlit application and user interaction
- `analytics.py` — Metric loading, validation, and supported calculations
- `build_metrics.py` — Logic for building aggregated metrics
- `metrics_summary.csv` — Aggregated data consumed by the application
- `requirements.txt` — Python dependencies
- `.streamlit/secrets.toml.example` — Safe template for local API configuration

### Metric Definitions

| Metric | Definition |
|---|---|
| Item sales | Sum of order-item prices, excluding freight |
| Order count | Number of orders represented by the relevant aggregation |
| Delivery variance | Actual customer delivery date minus estimated delivery date |
| Negative delivery variance | Delivery occurred earlier than estimated |
| Positive delivery variance | Delivery occurred later than estimated |

**Item sales are not profit.** The project should not be interpreted as measuring profit unless cost and expense data are incorporated into an explicit profit calculation.

The current overall row in `metrics_summary.csv` reports:

- **Item sales:** R$13,591,643.70
- **Orders:** 99,441
- **Average delivery variance:** −11.18 days

These figures describe the current aggregated metrics file. Comparisons across versions require consistent filters, aggregation logic, and metric definitions.

### Run the Application Locally

#### 1. Clone the repository

```bash
git clone https://github.com/VishnuKokkula/ecommerce-analytics.git
cd ecommerce-analytics/v3-ai-app
```

#### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use `.\venv\Scripts\python.exe` to run Python commands directly.

#### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### 4. Configure the Groq API key

Create a local secrets file by copying the example:

```powershell
Copy-Item .\.streamlit\secrets.toml.example .\.streamlit\secrets.toml
notepad .\.streamlit\secrets.toml
```

Replace the placeholder with your own Groq API key:

```toml
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
```

Get an API key from the official Groq Console: https://console.groq.com/

Never commit the real `secrets.toml` file or put an API key directly into source code.

#### 5. Start Streamlit

```powershell
python -m streamlit run app.py
```

Open the local URL shown in the terminal.

### How the AI-Assisted Workflow Works

1. The application loads aggregated metrics from `metrics_summary.csv`.
2. Python validates and calculates supported results.
3. Groq receives the calculated results and a request to explain them.
4. Streamlit displays the response.

The intended design separates numerical calculations from language generation. Unsupported questions should not be presented as verified answers. AI-generated explanations should not change the calculated values or introduce unsupported claims.

### Rebuilding Metrics

`build_metrics.py` contains the metric-building logic. Review the script's expected source-data paths and input files before rebuilding the aggregated CSV.

The source dataset files are not required to run the Streamlit app when the precomputed `metrics_summary.csv` is available.

Do not replace a validated metrics file without checking the resulting totals and metric definitions.

## Troubleshooting

**The app cannot find `metrics_summary.csv`**

Run Streamlit from `v3-ai-app` and verify that the CSV is present beside `app.py`.

**Groq requests fail**

Check your API key, model configuration, account access, API credits, rate limits, and network connection.

**The AI response is empty**

Inspect the API response and finish reason. A request completing without an API error does not guarantee readable response text.

**Excel and Power BI totals differ**

Compare filters, order-item aggregation, freight treatment, order-count logic, and delivery-date calculations before drawing conclusions.

## Limitations

- Results depend on the quality and scope of the underlying dataset.
- Item sales are not profit.
- Aggregated metrics cannot answer every question about individual orders or customers.
- AI explanations are limited by the calculations and context supplied to the model.
- Only implemented and verified calculation paths should be treated as supported analytical answers.

## Potential Improvements

- Additional deterministic analytical question types
- Automated data-quality and metric reconciliation tests
- More reproducible dependency management
- Expanded documented business metrics
- Improved automated testing

## Author

**VishnuTeja Kokkula**

Computer Science graduate interested in data analytics, business intelligence, and AI-powered applications.

- GitHub: https://github.com/VishnuKokkula
- Repository: https://github.com/VishnuKokkula/ecommerce-analytics
