import pandas as pd
from sqlalchemy import text
from db.connection import get_engine
from utils.logger import get_logger
 
logger = get_logger("silver.transformer.fakestore_products")
 
BRONZE_TABLE = "bronze.fakestore_products"
SILVER_TABLE = "silver.products_fakestore"
PRIMARY_KEY  = "product_id"
 
 
def extract() -> pd.DataFrame:
    """Read latest bronze records — deduplicated by product_id, keeping the most recent run."""
    sql = text(f"""
        SELECT DISTINCT ON (id)
            id, title, price, description, category,
            image, rating, _source, _ingested_at, _pipeline_run
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
        "id"    : "product_id",
        "image" : "image_url",
    })
  
    import json
    def safe_parse(val):
        if isinstance(val, dict):
            return val
        try:
            return json.loads(val)
        except Exception:
            return {}
 
    rating_parsed      = df["rating"].apply(safe_parse)
    df["rating_rate"]  = rating_parsed.apply(lambda x: x.get("rate"))
    df["rating_count"] = rating_parsed.apply(lambda x: x.get("count"))
    df = df.drop(columns=["rating"])
  
    df["product_id"]   = pd.to_numeric(df["product_id"],   errors="coerce").astype("Int64")
    df["price"]        = pd.to_numeric(df["price"],        errors="coerce")
    df["rating_rate"]  = pd.to_numeric(df["rating_rate"],  errors="coerce")
    df["rating_count"] = pd.to_numeric(df["rating_count"], errors="coerce").astype("Int64")
    df["_ingested_at"] = pd.to_datetime(df["_ingested_at"], utc=True, errors="coerce")
  
    before = len(df)
    df = df.dropna(subset=["product_id", "title", "price"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped} rows with null product_id / title / price")
  
    df = df[[
        "product_id", "title", "price", "description", "category",
        "image_url", "rating_rate", "rating_count",
        "_source", "_ingested_at", "_pipeline_run"
    ]]
 
    logger.info(f"Transformed {len(df)} rows for {SILVER_TABLE}")
    return df
 