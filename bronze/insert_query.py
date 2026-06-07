from db.connection import get_engine, get_connection
from sqlalchemy import text
from bronze.column_maps import rename_column_map
import json
import uuid
from pathlib import Path
import pandas as pd
from utils.logger import get_logger
 
logger = get_logger("bronze.insert_query")
  
 
def _prepare_fakestore_products(df: pd.DataFrame):
    
    df["rating"] = df.apply(
        lambda row: json.dumps({
            "rate": row["rating.rate"],
            "count": row["rating.count"]
        }), axis=1
    )
 
    df["id"]            = df["id"].astype(int)
    df["price"]         = df["price"].astype(str)
    df["_ingested_at"]  = pd.to_datetime(df["_ingested_at"], utc=True)
    df["_pipeline_run"] = df["_pipeline_run"].astype(str)
    df["_source"]       = df["_source"].astype(str)
 
    insert_cols = [
        "id", "title", "price", "description", "category",
        "image", "rating", "_source", "_ingested_at", "_pipeline_run"
    ]
 
    sql = text("""
        INSERT INTO bronze.fakestore_products (
            id, title, price, description, category,
            image, rating, _source, _ingested_at, _pipeline_run
        ) VALUES (
            :id, :title, :price, :description, :category,
            :image, :rating, :_source, :_ingested_at, :_pipeline_run
        )
    """)
 
    return df, insert_cols, sql
 
 
def _prepare_dummyjson_products(df: pd.DataFrame):
    
    df["id"] = df["id"].astype(int)
 
    text_cols = [
        "price", "discountPercentage", "rating", "stock", "weight",
        "minimumOrderQuantity", "_source", "_pipeline_run"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
 
    df["_ingested_at"] = pd.to_datetime(df["_ingested_at"], utc=True)
 
    insert_cols = [
        "id", "title", "description", "category", "price",
        "discountPercentage", "rating", "stock",
        "brand", "sku", "weight",
        "warrantyInformation", "shippingInformation",
        "availabilityStatus", "returnPolicy",
        "minimumOrderQuantity",
        "thumbnail", "_source", "_ingested_at", "_pipeline_run"
    ]
 
    sql = text("""
        INSERT INTO bronze.dummyjson_products (
            id, title, description, category, price,
            "discountPercentage", rating, stock,
            brand, sku, weight,
            "warrantyInformation", "shippingInformation",
            "availabilityStatus", "returnPolicy",
            "minimumOrderQuantity",
            thumbnail, _source, _ingested_at, _pipeline_run
        ) VALUES (
            :id, :title, :description, :category, :price,
            :discountPercentage, :rating, :stock,
            :brand, :sku, :weight,
            :warrantyInformation, :shippingInformation,
            :availabilityStatus, :returnPolicy,
            :minimumOrderQuantity,
            :thumbnail, :_source, :_ingested_at, :_pipeline_run
        )
    """)
 
    return df, insert_cols, sql
 
 
def _prepare_dummyjson_users(df: pd.DataFrame):
    
    json_cols = ["hair", "address", "bank", "company", "crypto"]
    for col in json_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if pd.notnull(x) else None
            )
 
    df["id"]            = df["id"].astype(int)
    df["_source"]       = df["_source"].astype(str)
    df["_pipeline_run"] = df["_pipeline_run"].astype(str)
    df["_ingested_at"]  = pd.to_datetime(df["_ingested_at"], utc=True)
 
    insert_cols = [
        "id", "firstName", "lastName", "maidenName",
        "age", "gender", "email", "phone", "username",
        "password", "birthDate", "image", "bloodGroup",
        "height", "weight", "eyeColor", "ip",
        "macAddress", "university",
        "ein", "ssn", "userAgent",
        "role", "_source", "_ingested_at", "_pipeline_run"
    ]
 
    sql = text("""
        INSERT INTO bronze.dummyjson_users (
            id, "firstName", "lastName", "maidenName",
            age, gender, email, phone, username,
            password, "birthDate", image, "bloodGroup",
            height, weight, "eyeColor", ip,
            "macAddress", university,
            ein, ssn, "userAgent",
            role, _source, _ingested_at, _pipeline_run
        ) VALUES (
            :id, :firstName, :lastName, :maidenName,
            :age, :gender, :email, :phone, :username,
            :password, :birthDate, :image, :bloodGroup,
            :height, :weight, :eyeColor, :ip,
            :macAddress, :university,
            :ein, :ssn, :userAgent,
            :role, :_source, :_ingested_at, :_pipeline_run
        )
    """)
 
    return df, insert_cols, sql
 
 
def _prepare_dummyjson_carts(df: pd.DataFrame):
    df["id"] = df["id"].astype(int)
 
    text_cols = [
        "userId", "total", "discountedTotal", "totalQuantity",
        "_source", "_pipeline_run"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
 
    df["_ingested_at"] = pd.to_datetime(df["_ingested_at"], utc=True)
 
    insert_cols = [
        "id", "userId",
        "total", "discountedTotal", "totalQuantity",
        "_source", "_ingested_at", "_pipeline_run"
    ]
 
    sql = text("""
        INSERT INTO bronze.dummyjson_carts (
            id, "userId",
            total, "discountedTotal", "totalQuantity",
            _source, _ingested_at, _pipeline_run
        ) VALUES (
            :id, :userId,
            :total, :discountedTotal, :totalQuantity,
            :_source, :_ingested_at, :_pipeline_run
        )
    """)
 
    return df, insert_cols, sql
 
 
def _prepare_jsonplaceholder_posts(df: pd.DataFrame):
    df["id"]            = df["id"].astype(int)
    df["userId"]        = df["userId"].astype(str)
    df["_source"]       = df["_source"].astype(str)
    df["_pipeline_run"] = df["_pipeline_run"].astype(str)
    df["_ingested_at"]  = pd.to_datetime(df["_ingested_at"], utc=True)
 
    insert_cols = [
        "id", "userId", "title", "body",
        "_source", "_ingested_at", "_pipeline_run"
    ]
 
    sql = text("""
        INSERT INTO bronze.jsonplaceholder_posts (
            id, "userId", title, body,
            _source, _ingested_at, _pipeline_run
        ) VALUES (
            :id, :userId, :title, :body,
            :_source, :_ingested_at, :_pipeline_run
        )
    """)
 
    return df, insert_cols, sql
 
  
TABLE_PREPARERS = {
    "bronze.fakestore_products"    : _prepare_fakestore_products,
    "bronze.dummyjson_products"    : _prepare_dummyjson_products,
    "bronze.dummyjson_users"       : _prepare_dummyjson_users,
    "bronze.dummyjson_carts"       : _prepare_dummyjson_carts,
    "bronze.jsonplaceholder_posts" : _prepare_jsonplaceholder_posts,
}
 
 
def _get_table_config(table: str, df: pd.DataFrame):
    preparer = TABLE_PREPARERS.get(table)
    if preparer is None:
        raise ValueError(
            f"No preparer registered for table: '{table}'. "
            f"Available: {list(TABLE_PREPARERS.keys())}"
        ) 
    return preparer(df)
 
  
 
def insert_dataframe(df: pd.DataFrame, table: str) -> int:
    if df.empty:
        logger.info(f"[{table}] DataFrame is empty, skipping insert.")
        return 0
 
    try:
        df = df.copy()
        df, insert_cols, sql = _get_table_config(table, df)
 
        missing = [col for col in insert_cols if col not in df.columns]
        if missing:
            raise ValueError(f"[{table}] DataFrame missing required columns: {missing}") 
 
        records = (
            df[insert_cols]
            .where(pd.notna(df[insert_cols]), None)
            .to_dict(orient="records")
        )
 
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(sql, records)
 
        logger.info(f"[{table}] Inserted {len(records)} rows.")
        return len(records)
 
    except ValueError as ve:
        logger.error(f"[insert_dataframe] Validation error: {ve}")
        raise
 
    except Exception as e:
        logger.error(f"[insert_dataframe] Failed to insert into {table}: {e}")
        raise
  
 
def ensure_table_exists(full_table_name: str) -> bool:
    engine = get_engine()
 
    if "." not in full_table_name:
        raise ValueError("Table must be in format 'schema.table'")
 
    schema, table = full_table_name.strip().split(".", 1)
    schema, table = schema.lower(), table.lower()
 
    def check_schema_exists(conn) -> bool:
        query = text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.schemata
                WHERE schema_name = :schema
            );
        """)
        return conn.execute(query, {"schema": schema}).scalar()
 
    def check_table_exists(conn) -> bool:
        query = text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = :schema
                  AND table_name   = :table
            );
        """)
        return conn.execute(query, {"schema": schema, "table": table}).scalar()
 
    base_dir       = Path(__file__).resolve().parent
    migration_file = base_dir.parent / "db" / "migrations" / "bronze_tables.sql"
 
    with engine.begin() as conn:
        if not check_schema_exists(conn):
            logger.info(f"Schema '{schema}' not found — creating...")
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
 
        if check_table_exists(conn):
            logger.info(f"Table '{schema}.{table}' already exists.")
            return True
 
        logger.info(f"Table '{schema}.{table}' not found — running migration...")
 
        if not migration_file.exists():
            raise FileNotFoundError(f"Migration file not found: {migration_file}")
 
        with open(migration_file, "r", encoding="utf-8") as f:
            sql_script = f.read()
 
        conn.execute(text(sql_script))
        logger.info(f"Migration executed from: {migration_file}")
 
        created = check_table_exists(conn)
        if not created:
            raise RuntimeError(
                f"Migration ran but '{schema}.{table}' still not found. "
                f"Check that {migration_file.name} creates this table."
            )
 
        logger.info(f"Table '{schema}.{table}' created successfully.")
        return True
        
def log_pipeline_run(
    run_id: str,
    source_name: str,
    status: str,
    rows_inserted: int | None = None,
    error_message: str | None = None,
    started_at=None,
    finished_at=None,
) -> None:
    engine = get_engine()
    insert_sql = text("""
        INSERT INTO bronze.pipeline_run_log
            (run_id, source_name, status, rows_inserted, error_message, started_at, finished_at)
        VALUES
            (:run_id, :source_name, :status, :rows_inserted, :error_message, :started_at, :finished_at)
    """)
 
    params = {
        "run_id"        : run_id,
        "source_name"   : source_name,
        "status"        : status,
        "rows_inserted" : rows_inserted,
        "error_message" : error_message,
        "started_at"    : started_at,
        "finished_at"   : finished_at,
    }
 
    try:
        with engine.begin() as conn:
            conn.execute(insert_sql, params)
        logger.info(f"[{source_name}] Logged pipeline run {run_id} ({status})")
    except Exception as e:
        logger.error(f"Failed to log pipeline run: {e}")