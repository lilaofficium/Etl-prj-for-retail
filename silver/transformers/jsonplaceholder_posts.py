import pandas as pd
from sqlalchemy import text
from db.connection import get_engine
from utils.logger import get_logger
 
logger = get_logger("silver.transformer.jsonplaceholder_posts")
 
BRONZE_TABLE = "bronze.jsonplaceholder_posts"
SILVER_TABLE = "silver.posts"
PRIMARY_KEY  = "post_id"
 
 
def extract() -> pd.DataFrame:
    sql = text(f"""
        SELECT DISTINCT ON (id)
            id, "userId", title, body,
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
        "id"     : "post_id",
        "userId" : "user_id",
    })
  
    df["post_id"]      = pd.to_numeric(df["post_id"],  errors="coerce").astype("Int64")
    df["user_id"]      = pd.to_numeric(df["user_id"],  errors="coerce").astype("Int64")
    df["_ingested_at"] = pd.to_datetime(df["_ingested_at"], utc=True, errors="coerce")
  
    before = len(df)
    df = df.dropna(subset=["post_id", "title"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped} rows with null post_id / title")
  
    df = df[[
        "post_id", "user_id", "title", "body",
        "_source", "_ingested_at", "_pipeline_run"
    ]]
 
    logger.info(f"Transformed {len(df)} rows for {SILVER_TABLE}")
    return df