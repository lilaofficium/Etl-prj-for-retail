import pandas as pd
from sqlalchemy import text
from db.connection import get_engine
from utils.logger import get_logger
 
logger = get_logger("silver.transformer.dummyjson_carts")
 
BRONZE_TABLE = "bronze.dummyjson_carts"
SILVER_TABLE = "silver.carts"
PRIMARY_KEY  = "cart_id"
 
 
def extract() -> pd.DataFrame:
    sql = text(f"""
        SELECT DISTINCT ON (id)
            id, "userId", total, "discountedTotal", "totalQuantity",
            _source, _ingested_at, _pipeline_run
        FROM {BRONZE_TABLE}
        ORDER BY id, _ingested_at DESC
    """)
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
    logger.info(f"Extracted {len(df)} rows from {BRONZE_TABLE}")
    return df
 
 
def transform(df: pd.DataFrame) -> pd.DataFrame: 
    df = df.rename(columns={
        "id"              : "cart_id",
        "userId"          : "user_id",
        "discountedTotal" : "discounted_total",
        "totalQuantity"   : "total_quantity",
    })
  
    df["cart_id"]         = pd.to_numeric(df["cart_id"],         errors="coerce").astype("Int64")
    df["user_id"]         = pd.to_numeric(df["user_id"],         errors="coerce").astype("Int64")
    df["total"]           = pd.to_numeric(df["total"],           errors="coerce")
    df["discounted_total"] = pd.to_numeric(df["discounted_total"], errors="coerce")
    df["total_quantity"]  = pd.to_numeric(df["total_quantity"],  errors="coerce").astype("Int64")
    df["_ingested_at"]    = pd.to_datetime(df["_ingested_at"], utc=True, errors="coerce")
  
    before = len(df)
    df = df.dropna(subset=["cart_id", "user_id"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped} rows with null cart_id / user_id")
  
    df = df[[
        "cart_id", "user_id",
        "total", "discounted_total", "total_quantity",
        "_source", "_ingested_at", "_pipeline_run"
    ]]
 
    logger.info(f"Transformed {len(df)} rows for {SILVER_TABLE}")
    return df