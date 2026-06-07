import pandas as pd
from sqlalchemy import text
from db.silver_connection import get_silver_engine
from utils.logger import get_logger
from datetime import datetime, timezone
 
logger = get_logger("silver.transformer.joiner")
 
SILVER_TABLE = "silver.cart_user_summary"
 
 
def build_cart_user_summary(run_id: str) -> pd.DataFrame:
    """
    Join silver.carts with silver.users to produce a flat summary table.
    This runs AFTER all individual transformers have loaded their data.
 
    Why join here and not in bronze?
    - Bronze stores raw data per source — no joins.
    - Silver is the first layer where data is clean and typed, making joins safe.
    - Gold layer will use this summary for aggregated KPIs.
    """
    sql = text("""
        SELECT
            c.cart_id,
            c.user_id,
            u.first_name,
            u.last_name,
            u.email,
            c.total,
            c.discounted_total,
            c.total_quantity
        FROM silver.carts c
        LEFT JOIN silver.users u ON c.user_id = u.user_id
        ORDER BY c.cart_id
    """)
 
    engine = get_silver_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
 
    logger.info(f"Joined {len(df)} cart+user rows")
  
    df["_pipeline_run"]     = run_id
    df["_silver_loaded_at"] = datetime.now(timezone.utc)
 
    return df