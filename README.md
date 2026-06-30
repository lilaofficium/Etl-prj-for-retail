# Retail ETL Pipeline — Medallion Architecture

> End-to-end ETL pipeline built with Python and PostgreSQL using the **Medallion Architecture** (Bronze → Silver → Gold).
> Simulates a real enterprise data warehouse workflow for a retail business.

---

## Table of Contents

- [The Problem This Solves](#the-problem-this-solves)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Actual Bronze Execution Flow](#actual-bronze-execution-flow)
- [Key Engineering Features](#key-engineering-features)
- [How to Run](#how-to-run)
- [Business KPIs Available (Gold Layer)](#business-kpis-available-gold-layer)
- [What I Learned Building This](#what-i-learned-building-this)
- [Known Limitations / Honest Notes](#known-limitations--honest-notes)
- [Roadmap / Next Version](#roadmap--next-version)
- [Author](#author)
- [Tags](#tags)

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
  [REST APIs: FakeStore, DummyJSON, JSONPlaceholder]
                    │
                    ▼
            ┌─────────────┐
            │   BRONZE    │  ← Raw load, no transformation
            │  (staging)  │    Tracks source, ingestion time, run_id
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
| PostgreSQL | — | Data warehouse (separate DB per layer) |
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
│   ├── pipeline.py          ← run_bronze_pipeline() — orchestrates the source loop
│   ├── extractor.py         ← get_api_data() — paginated/non-paginated REST extraction with retry
│   ├── loader.py            ← add_metadata(), save_to_bronze()
│   ├── insert_query.py      ← ensure_table_exists(), insert_dataframe(), per-table preparers
│   └── column_maps.py       ← per-source column rename maps (not currently wired into the pipeline)
│
├── silver/
│   └── pipeline.py          ← Cleaning, validation, upserts
│
├── gold/
│   └── pipeline.py          ← Dimensional model & KPI tables
│
├── run_layer/                ← run_bronze.py / run_silver.py / run_gold.py — standalone layer runners
│
├── db/
│   ├── connection.py        ← Bronze DB engine/connection
│   ├── silver_connection.py ← Silver DB engine/connection
│   ├── gold_connection.py   ← Gold DB engine/connection
│   └── migrations/          ← bronze_tables.sql, silver_tables.sql, gold_tables.sql
│
├── config/
│   ├── settings.py          ← Pydantic Settings (.env-driven DB configs per layer)
│   └── sources.yaml         ← API source definitions (url, data_key, format)
│
├── utils/
│   └── logger.py            ← Shared file-based logger
│
├── storage/
│   └── bronze/              ← Local file storage for raw data
│
├── logs/                     ← Pipeline execution logs (date-stamped)
├── insert_errors.log         ← Tracks failed inserts
├── insert_queries.log        ← Tracks executed SQL
│
├── requirements.txt
└── .gitignore
```

---

## How It Works

### Step 1 — Bronze (Raw Ingestion)
- Reads source config from `config/sources.yaml` (URL, pagination key, format)
- Extracts data from REST APIs with retry + exponential backoff
- Loads data as-is into Bronze PostgreSQL tables, with no business transformation
- Each row is stamped with `_source`, `_ingested_at`, and `_pipeline_run`
- Each run is tracked with a unique `PIPELINE_RUN_ID` (UUID), logged per source in `bronze.pipeline_run_log`

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
# Each run gets a unique ID for traceability — shared across all 3 layers
os.environ["PIPELINE_RUN_ID"] = str(uuid.uuid4())

run_bronze_pipeline()   # ingest raw
run_silver_pipeline()   # clean + validate
run_gold_pipeline()     # build reporting layer
```

> Note: standalone layer runners (`run_bronze.py`, `run_silver.py`, `run_gold.py` in `run_layer/`) generate their own prefixed run IDs (`silver-{uuid}`, `gold-{uuid}`) when run independently, separate from the shared ID used by `main.py`.

---

## Actual Bronze Execution Flow

This is the verified, code-level trace of what happens on every bronze run, file by file.

**1. Entry point — `main.py` or `run_layer/run_bronze.py`**
A `PIPELINE_RUN_ID` is generated with `uuid.uuid4()` and set as an environment variable **before** the pipeline is invoked. It is read by the pipeline, not created inside it.

**2. `bronze/pipeline.py` → `run_bronze_pipeline()`**
- Opens and parses `config/sources.yaml`
- Reads `run_id` from the environment (defaults to `"local"` if unset — e.g. if the function is imported and called directly)
- Loops over every entry under `sources:` in the YAML
- For each source, wrapped in try/except:
  1. `get_api_data(url, params=None, data_key=cfg.get("data_key"))`
  2. `add_metadata(raw_records, source_name, run_id)`
  3. `save_to_bronze(enriched, source_name, run_id)`
  4. `log_pipeline_run(...)` — recorded on both success and failure

**3. `bronze/extractor.py` → `get_api_data()`**
- Calls `_fetch_with_retry()`, retrying up to `api_retry_count` times with exponential backoff (`api_retry_backoff ** attempt`), both configured in `config/settings.py`
- Auto-detects pagination: if the response is a dict containing `"total"`, it loops fetching `limit`/`skip` pages until all records are collected; otherwise treats the response as a flat list or single dict keyed by `data_key`
- Returns a flattened `pandas.DataFrame` via `pd.json_normalize`

**4. `bronze/loader.py` → `add_metadata()`**
Stamps three audit columns onto every row:
- `_source` — the source name from config
- `_ingested_at` — UTC ISO timestamp of ingestion
- `_pipeline_run` — the run_id

**5. `bronze/loader.py` → `save_to_bronze()`**
- Resolves the target table from a static `TABLE_MAP` dict (e.g. `fakestore_products` → `bronze.fakestore_products`)
- Calls `ensure_table_exists(table)`; only proceeds to insert if it returns `True`
- Calls `insert_dataframe(df, table)` and returns the row count

**6. `bronze/insert_query.py` → `ensure_table_exists()`**
- Checks `information_schema.schemata` for the schema, creates it with `CREATE SCHEMA IF NOT EXISTS` if missing
- Checks `information_schema.tables` for the table
- If missing, runs the **entire** `db/migrations/bronze_tables.sql` migration file (not a single-table `CREATE`), then re-verifies the table now exists

**7. `bronze/insert_query.py` → `insert_dataframe()`**
- Calls `_get_table_config(table, df)`, which dispatches to a per-table "preparer" function via the `TABLE_PREPARERS` dict (one function per source, e.g. `_prepare_fakestore_products`, `_prepare_dummyjson_users`)
- Each preparer: casts ID columns to int, stringifies select fields, JSON-encodes nested objects (e.g. `rating`, `address`, `bank`, `crypto`), defines the exact `insert_cols` list, and builds the parameterized `INSERT` SQL statement
- Back in `insert_dataframe`: validates all `insert_cols` exist in the DataFrame, converts rows to a list of dicts (`NaN` → `None`), and executes the insert inside a single `engine.begin()` transaction

**8. Run logging**
Every source's outcome (success or failure) is written to `bronze.pipeline_run_log` via `log_pipeline_run()`, including `started_at`, `finished_at`, row count, and error message if applicable.

```
config/sources.yaml
        │
        ▼
run_bronze_pipeline()  ──loop per source──▶ get_api_data()  ──▶  add_metadata()
        │                                                              │
        │                                                              ▼
        │                                                      save_to_bronze()
        │                                                              │
        │                                            ┌─────────────────┴─────────────────┐
        │                                            ▼                                    ▼
        │                                  ensure_table_exists()                 insert_dataframe()
        │                                                                                  │
        │                                                                                  ▼
        │                                                                       _get_table_config()
        │                                                                        (per-table preparer)
        ▼
log_pipeline_run()  ◀── success or failure, every source
```

---

## Key Engineering Features

- **Retry with exponential backoff** on API extraction failures
- **Automatic pagination handling** for paginated REST sources
- **Audit columns on every row** — `_source`, `_ingested_at`, `_pipeline_run`
- **Self-healing schema/table creation** — bronze tables are created from migration SQL on first run
- **Per-run audit logging** — every source's success/failure is logged to `bronze.pipeline_run_log`
- **Upsert logic in Silver** — handles late-arriving or updated data correctly
- **Pydantic validation** — bad data is caught before entering Silver
- **Structured logging** — every run is tracked with errors and query logs
- **Config-driven sources** — change API URLs and pagination keys via YAML, no code changes
- **UUID-based run tracking** — every pipeline execution has a unique ID for debugging
- **Separated concerns** — Bronze / Silver / Gold each have their own pipeline module and database

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
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=retail_bronze_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

SILVER_POSTGRES_HOST=localhost
SILVER_POSTGRES_PORT=5432
SILVER_POSTGRES_DB=retail_silver_db
SILVER_POSTGRES_USER=your_user
SILVER_POSTGRES_PASSWORD=your_password

GOLD_POSTGRES_HOST=localhost
GOLD_POSTGRES_PORT=5432
GOLD_POSTGRES_DB=retail_gold_db
GOLD_POSTGRES_USER=your_user
GOLD_POSTGRES_PASSWORD=your_password
```

### 5. Run the full pipeline
```bash
python main.py
```

Or run a single layer independently:
```bash
python run_layer/run_bronze.py
python run_layer/run_silver.py
python run_layer/run_gold.py
```

### Expected output
```
Starting Bronze Pipeline...
===== BRONZE PIPELINE SUMMARY =====
  success  fakestore_products         20 rows loaded
  success  dummyjson_products        194 rows loaded
  success  dummyjson_users            30 rows loaded
  success  dummyjson_carts            20 rows loaded
  success  jsonplaceholder_posts     100 rows loaded
==================================================

Starting Silver Pipeline...
===== SILVER PIPELINE SUMMARY =====
  success  products                  214 rows upserted
  success  users                      30 rows upserted
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
- Config-driven pipeline design — separating source configuration from code
- UUID-based pipeline run tracking for debugging and audit trails
- Building retry/backoff and pagination handling for real-world REST APIs

---

## Known Limitations / Honest Notes

A few things worth being upfront about (and good talking points in interviews):

- `bronze/column_maps.py` defines per-source column rename mappings, but it isn't currently called anywhere in the pipeline — column selection and renaming for inserts is instead handled inside the per-table preparer functions in `insert_query.py`. This is leftover/unused scaffolding.
- Table schema is not actually YAML-driven — only API source URLs and pagination config live in `sources.yaml`. Column definitions and insert logic are hardcoded per table in `TABLE_PREPARERS`.
- `ensure_table_exists()` re-runs the entire `bronze_tables.sql` migration file when any single table is missing, rather than creating just the missing table.
- Run-ID format differs slightly between `main.py` (bare UUID, shared across all layers) and the standalone `run_layer/run_*.py` scripts (layer-prefixed UUIDs).

---

## Roadmap / Next Version

- [ ] Add Apache Airflow for scheduled orchestration
- [ ] Add dbt for Silver → Gold transformations
- [ ] Add Docker + docker-compose for one-command setup
- [ ] Connect Gold layer to Power BI with live dashboard screenshots
- [ ] Add Great Expectations for automated data quality checks
- [ ] Add unit tests for transformation logic
- [ ] Wire up or remove `column_maps.py`
- [ ] Make `ensure_table_exists()` create only the missing table, not the whole migration file

---

## Author

**Lila Yadav**
Data Engineer | 5+ years Software Engineering Experience

- GitHub: [github.com/lilaofficium](https://github.com/lilaofficium)
- LinkedIn: [lila-kumari-yadav](https://www.linkedin.com/in/lila-kumari-yadav-476926228/)

---

## Tags

`python` `postgresql` `etl` `data-engineering` `medallion-architecture`
`sqlalchemy` `pandas` `pydantic` `data-warehouse` `data-pipeline`
