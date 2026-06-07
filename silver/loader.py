import pandas as pd
from sqlalchemy import text
from db.silver_connection import get_silver_engine
from utils.logger import get_logger
 
logger = get_logger("silver.loader")
 
 
def upsert_to_silver(df: pd.DataFrame, table: str, primary_key: str) -> int:
    
    if df.empty:
        logger.info(f"[{table}] Empty DataFrame — skipping.")
        return 0
 
    cols        = list(df.columns)
    update_cols = [c for c in cols if c != primary_key]
 
    col_list    = ", ".join(f'"{c}"' for c in cols)
    val_list    = ", ".join(f":{c}"  for c in cols)
    update_set  = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in update_cols)
 
    sql = text(f"""
        INSERT INTO {table} ({col_list})
        VALUES ({val_list})
        ON CONFLICT ("{primary_key}") DO UPDATE SET {update_set}
    """)
 
    records = df.where(pd.notna(df), None).to_dict(orient="records")
    engine  = get_silver_engine()
 
    with engine.begin() as conn:
        conn.execute(sql, records)
 
    logger.info(f"[{table}] Upserted {len(records)} rows.")
    return len(records)
 
 
def truncate_and_insert(df: pd.DataFrame, table: str) -> int:
   
    if df.empty:
        logger.info(f"[{table}] Empty DataFrame — skipping.")
        return 0
 
    engine = get_silver_engine()
 
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table}"))
 
    cols     = list(df.columns)
    col_list = ", ".join(f'"{c}"' for c in cols)
    val_list = ", ".join(f":{c}"  for c in cols)
    sql      = text(f"INSERT INTO {table} ({col_list}) VALUES ({val_list})")
 
    records = df.where(pd.notna(df), None).to_dict(orient="records")
 
    with engine.begin() as conn:
        conn.execute(sql, records)
 
    logger.info(f"[{table}] Truncated and inserted {len(records)} rows.")
    return len(records)