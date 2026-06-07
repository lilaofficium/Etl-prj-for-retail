import pandas as pd
from sqlalchemy import text
from db.silver_connection import get_silver_engine
from utils.logger import get_logger
 
logger = get_logger("gold.aggregator.user_demographics")
 
GOLD_TABLE = "gold.user_demographics"
 
 
def build(run_id: str) -> pd.DataFrame:
    """
    Age group + gender breakdown of the user base from silver.users.
    Age groups: 18-24, 25-34, 35-44, 45-54, 55+
    Useful for understanding customer segmentation at a glance.
    """
    sql = text("""
        SELECT
            CASE
                WHEN age BETWEEN 18 AND 24 THEN '18-24'
                WHEN age BETWEEN 25 AND 34 THEN '25-34'
                WHEN age BETWEEN 35 AND 44 THEN '35-44'
                WHEN age BETWEEN 45 AND 54 THEN '45-54'
                ELSE '55+'
            END                             AS age_group,
            gender,
            COUNT(*)                        AS user_count,
            ROUND(AVG(age)::NUMERIC, 1)     AS avg_age
        FROM silver.users
        WHERE age IS NOT NULL AND gender IS NOT NULL
        GROUP BY age_group, gender
        ORDER BY age_group, gender
    """)
 
    engine = get_silver_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
 
    df["_pipeline_run"] = run_id
    logger.info(f"Built {len(df)} rows for {GOLD_TABLE}")
    return df