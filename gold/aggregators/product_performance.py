import pandas as pd
from sqlalchemy import text
from db.silver_connection import get_silver_engine
from utils.logger import get_logger
 
logger = get_logger("gold.aggregator.product_performance")
 
GOLD_TABLE = "gold.product_performance"
 
 
def build(run_id: str) -> pd.DataFrame:
    
    sql = text("""
        SELECT
            'dummyjson'  AS source,
            product_id,
            title,
            category,
            price,
            rating,
            stock,
            CASE
                WHEN rating >= 4.0 THEN 'top_rated'
                WHEN rating >= 2.5 THEN 'average'
                ELSE 'low_rated'
            END AS rating_tier,
            CASE
                WHEN stock = 0    THEN 'out_of_stock'
                WHEN stock <= 10  THEN 'low_stock'
                ELSE 'in_stock'
            END AS stock_status
        FROM silver.products_dummyjson
 
        UNION ALL
 
        SELECT
            'fakestore'  AS source,
            product_id,
            title,
            category,
            price,
            rating_rate  AS rating,
            NULL         AS stock,
            CASE
                WHEN rating_rate >= 4.0 THEN 'top_rated'
                WHEN rating_rate >= 2.5 THEN 'average'
                ELSE 'low_rated'
            END AS rating_tier,
            NULL         AS stock_status
        FROM silver.products_fakestore
 
        ORDER BY source, rating DESC
    """)
 
    engine = get_silver_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
 
    df["_pipeline_run"] = run_id
    logger.info(f"Built {len(df)} rows for {GOLD_TABLE}")
    return df