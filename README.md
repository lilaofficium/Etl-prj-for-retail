# Retail ETL Pipeline — Medallion Architecture

> End-to-end ETL pipeline built with Python and PostgreSQL using the **Medallion Architecture** (Bronze → Silver → Gold).
> Simulates a real enterprise data warehouse workflow for a retail business.

---

## The Problem This Solves

A retail business collects raw transactional data every day — orders, customers, products, returns.
The data arrives messy, duplicated, and unvalidated. Business teams need clean, reliable KPI reports
but cannot query the raw source directly.

This pipeline solves that by organizing data into three progressive layers:

| Layer | Purpose | State of Data |
|-------|---------|---------------|
| **Bronze** | Raw ingestion | As-is, untouched |
| **Silver** | Cleaning & validation | Deduplicated, validated, upserted |
| **Gold** | Business reporting | Dimensional model, KPI-ready |

---

## Architecture

```
  [Raw Data Source]
        │
        ▼
  ┌─────────────┐
  │   BRONZE    │  ← Raw load, no transformation
  │  (staging)  │    Tracks what came in and when
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │   SILVER    │  ← Clean, validate, deduplicate
  │  (trusted)  │    Upsert logic, Pydantic checks
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │    GOLD     │  ← Dimensional model
  │ (reporting) │    Fact + Dimension tables, KPIs
  └─────────────┘
        │
        ▼
  [Power BI / Analytics]
```

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.x | Pipeline orchestration |
| PostgreSQL | — | Data warehouse (all 3 layers) |
| SQLAlchemy | 2.0.50 | Database connection & ORM |
| Pandas | 3.0.3 | Data cleaning & transformation |
| Pydantic | 2.13.4 | Data validation & schema enforcement |
| pydantic-settings | 2.14.1 | Config-driven environment management |
| python-dotenv | 1.2.2 | Environment variable management |
| PyYAML | 6.0.3 | YAML configuration files |
| psycopg2-binary | 2.9.12 | PostgreSQL driver |
| requests | 2.34.2 | HTTP / REST API ingestion |
| NumPy | 2.4.6 | Numerical operations |

---

## Project Structure

```
Etl-prj-for-retail/
│
├── main.py                  ← Entry point — runs all 3 layers in sequence
│
├── bronze/
│   └── pipeline.py          ← Raw ingestion logic
│
├── silver/
│   └── pipeline.py          ← Cleaning, validation, upserts
│
├── gold/
│   └── pipeline.py          ← Dimensional model & KPI tables
│
├── run_layer/               ← Layer execution helpers
│
├── db/                      ← Database connection setup
│
├── config/                  ← YAML config files (source paths, table names)
│
├── utils/                   ← Shared utility functions
│
├── storage/
│   └── bronze/              ← Local file storage for raw data
│
├── logs/                    ← Pipeline execution logs
├── insert_errors.log        ← Tracks failed inserts
├── insert_queries.log       ← Tracks executed SQL
│
├── requirements.txt
└── .gitignore
```

---

## How It Works

### Step 1 — Bronze (Raw Ingestion)
- Reads raw data from CSV files or REST APIs
- Loads data as-is into Bronze PostgreSQL tables
- No transformation — preserves the original source data
- Each run is tracked with a unique `PIPELINE_RUN_ID` (UUID)

### Step 2 — Silver (Clean & Validate)
- Reads from Bronze tables
- Validates schema and data types using **Pydantic**
- Removes duplicates and handles null values
- Uses **upsert logic** — inserts new records, updates changed ones
- Rows are logged: how many upserted per table

### Step 3 — Gold (Business Reporting)
- Reads from Silver tables
- Builds a **dimensional model** (star schema)
- Creates fact and dimension tables for business KPIs
- Ready to connect directly to Power BI or any BI tool

### Pipeline Orchestration (`main.py`)
```python
# Each run gets a unique ID for traceability
os.environ["PIPELINE_RUN_ID"] = str(uuid.uuid4())

run_bronze_pipeline()   # ingest raw
run_silver_pipeline()   # clean + validate
run_gold_pipeline()     # build reporting layer
```

---

## Key Engineering Features

- **Incremental loading** — only processes new or changed records
- **Upsert logic** — handles late-arriving or updated data correctly
- **Pydantic validation** — bad data is caught before entering Silver
- **Structured logging** — every run is tracked with errors and query logs
- **Config-driven** — change source paths and table names via YAML, no code changes
- **UUID-based run tracking** — every pipeline execution has a unique ID for debugging
- **Separated concerns** — Bronze / Silver / Gold each have their own pipeline module

---

## How to Run

### 1. Clone the repo
```bash
git clone https://github.com/lilaofficium/Etl-prj-for-retail.git
cd Etl-prj-for-retail
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create a `.env` file in the root:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=retail_db
DB_USER=your_user
DB_PASSWORD=your_password
```

### 5. Run the full pipeline
```bash
python main.py
```

### Expected output
```
Starting Bronze Pipeline...
===== BRONZE PIPELINE SUMMARY =====
  success  orders                    1250 rows loaded
  success  customers                  430 rows loaded
==================================================

Starting Silver Pipeline...
===== SILVER PIPELINE SUMMARY =====
  success  orders                    1248 rows upserted
  success  customers                  430 rows upserted
==================================================

Starting Gold Pipeline...
===== GOLD PIPELINE SUMMARY =====
  success  fact_orders               1248 rows loaded
  success  dim_customer               430 rows loaded
==================================================

All pipelines completed.
```

---

## Business KPIs Available (Gold Layer)

- Total revenue by month, category, and region
- Top customers by lifetime value
- Product-level return rate
- Average order value over time
- Daily and weekly sales summaries

---

## What I Learned Building This

- Designing a Medallion Architecture (Bronze / Silver / Gold) from scratch
- Writing incremental load and upsert logic in PostgreSQL
- Using Pydantic for data contract enforcement before Silver ingestion
- Structuring a Python ETL project the way a real engineering team would
- Config-driven pipeline design — separating configuration from code
- UUID-based pipeline run tracking for debugging and audit trails

---

## Roadmap / Next Version

- [ ] Add Apache Airflow for scheduled orchestration
- [ ] Add dbt for Silver → Gold transformations
- [ ] Add Docker + docker-compose for one-command setup
- [ ] Connect Gold layer to Power BI with live dashboard screenshots
- [ ] Add Great Expectations for automated data quality checks
- [ ] Add unit tests for transformation logic

---

## Author

**Lila Yadav**
Data Engineer | 5+ years Software Engineering Experience

- GitHub: [github.com/lilaofficium](https://github.com/lilaofficium)
- LinkedIn: *(https://www.linkedin.com/in/lila-kumari-yadav-476926228/)*

---

## Tags

`python` `postgresql` `etl` `data-engineering` `medallion-architecture`
`sqlalchemy` `pandas` `pydantic` `data-warehouse` `data-pipeline`
