import pandas as pd
from sqlalchemy import text
from db.gold_connection import get_gold_engine
from utils.logger import get_logger
 
logger = get_logger("gold.loader")
 
 
def load_to_gold(df: pd.DataFrame, table: str) -> int:
     
    if df.empty:
        logger.info(f"[{table}] Empty DataFrame — skipping.")
        return 0
 
    engine = get_gold_engine()
 
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table}"))
 
    cols     = list(df.columns)
    col_list = ", ".join(f'"{c}"' for c in cols)
    val_list = ", ".join(f":{c}"  for c in cols)
    sql      = text(f"INSERT INTO {table} ({col_list}) VALUES ({val_list})")
 
    records = df.where(pd.notna(df), None).to_dict(orient="records")
 
    with engine.begin() as conn:
        conn.execute(sql, records)
 
    logger.info(f"[{table}] Loaded {len(records)} rows.")
    return len(records)