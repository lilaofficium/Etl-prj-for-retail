import pandas as pd
from sqlalchemy import text
from db.silver_connection import get_silver_engine
from utils.logger import get_logger
 
logger = get_logger("gold.aggregator.post_activity")
 
GOLD_TABLE = "gold.post_activity"
 
 
def build(run_id: str) -> pd.DataFrame:
    """
    Posts per user — joins silver.posts with silver.users.
    Users with 0 posts are included via LEFT JOIN.
    Ordered by post_count descending so most active users appear first.
    """
    sql = text("""
        SELECT
            u.user_id,
            u.first_name,
            u.last_name,
            u.email,
            COUNT(p.post_id)    AS post_count
        FROM silver.users u
        LEFT JOIN silver.posts p ON u.user_id = p.user_id
        GROUP BY u.user_id, u.first_name, u.last_name, u.email
        ORDER BY post_count DESC
    """)
 
    engine = get_silver_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
 
    df["_pipeline_run"] = run_id
    logger.info(f"Built {len(df)} rows for {GOLD_TABLE}")
    return df