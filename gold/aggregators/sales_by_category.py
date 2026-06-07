import pandas as pd
from sqlalchemy import text
from db.silver_connection import get_silver_engine
from utils.logger import get_logger
 
logger = get_logger("gold.aggregator.sales_by_category")
 
GOLD_TABLE = "gold.sales_by_category"
 
 
def build(run_id: str) -> pd.DataFrame:
    """
    Aggregate dummyjson products by category.
    Produces: avg price, avg discount, avg rating, total stock, and a price band label.
 
    Price bands:
      budget  = avg_price < 20
      mid     = avg_price 20–100
      premium = avg_price > 100
    """
    sql = text("""
        SELECT
            category,
            COUNT(*)                            AS total_products,
            ROUND(AVG(price)::NUMERIC, 2)       AS avg_price,
            ROUND(AVG(discount_percentage)::NUMERIC, 2) AS avg_discount_pct,
            ROUND(AVG(rating)::NUMERIC, 2)      AS avg_rating,
            SUM(stock)                          AS total_stock,
            CASE
                WHEN AVG(price) < 20   THEN 'budget'
                WHEN AVG(price) <= 100 THEN 'mid'
                ELSE 'premium'
            END                                 AS price_band
        FROM silver.products_dummyjson
        GROUP BY category
        ORDER BY avg_price DESC
    """)
 
    engine = get_silver_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
 
    df["_pipeline_run"] = run_id
    logger.info(f"Built {len(df)} rows for {GOLD_TABLE}")
    return df