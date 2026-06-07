import pandas as pd
from sqlalchemy import text
from db.silver_connection import get_silver_engine
from utils.logger import get_logger
 
logger = get_logger("gold.aggregator.top_spenders")
 
GOLD_TABLE = "gold.top_spenders"
 
 
def build(run_id: str) -> pd.DataFrame:
    """
    Rank users by total spend using the cart_user_summary join table.
    Produces: total carts, total spent, total savings, avg cart value.
    Ordered by total_spent descending so the top row = highest spender.
    """
    sql = text("""
        SELECT
            user_id,
            first_name,
            last_name,
            email,
            COUNT(cart_id)                              AS total_carts,
            ROUND(SUM(total)::NUMERIC, 2)               AS total_spent,
            ROUND(SUM(discounted_total)::NUMERIC, 2)    AS total_discounted,
            ROUND((SUM(total) - SUM(discounted_total))::NUMERIC, 2) AS total_savings,
            SUM(total_quantity)                         AS total_items,
            ROUND(AVG(total)::NUMERIC, 2)               AS avg_cart_value
        FROM silver.cart_user_summary
        GROUP BY user_id, first_name, last_name, email
        ORDER BY total_spent DESC
    """)
 
    engine = get_silver_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
 
    df["_pipeline_run"] = run_id
    logger.info(f"Built {len(df)} rows for {GOLD_TABLE}")
    return df