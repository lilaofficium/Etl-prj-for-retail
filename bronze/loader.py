from utils.logger import get_logger
from bronze.insert_query import insert_dataframe, ensure_table_exists, log_pipeline_run
import pandas as pd
from datetime import datetime, timezone

logger = get_logger("bronze.loader") 

TABLE_MAP = {
    "fakestore_products"    : "bronze.fakestore_products",
    "dummyjson_products"    : "bronze.dummyjson_products",
    "dummyjson_users"       : "bronze.dummyjson_users",
    "dummyjson_carts"       : "bronze.dummyjson_carts",
    "jsonplaceholder_posts" : "bronze.jsonplaceholder_posts",
}


def save_to_bronze(df: pd.DataFrame, source_name: str, run_id: str) -> int:
    table = TABLE_MAP.get(source_name)
    if not table:
        raise ValueError(f"No table mapped for source: {source_name}")

    table_ready = ensure_table_exists(table)

    if not table_ready:
        raise RuntimeError(f"Table {table} could not be created or verified. Aborting insert.")

    rows_inserted = insert_dataframe(df, table)
    logger.info(f"[{source_name}] Inserted {rows_inserted} rows into {table}")
    return rows_inserted


def add_metadata(df: pd.DataFrame, source_name: str, run_id: str) -> pd.DataFrame:
    ingestion_time = datetime.now(timezone.utc).isoformat()

    df = df.copy()
    df["_source"]       = source_name
    df["_ingested_at"]  = ingestion_time
    df["_pipeline_run"] = run_id
    return df
