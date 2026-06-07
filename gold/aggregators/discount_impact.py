import pandas as pd
from sqlalchemy import text
from db.silver_connection import get_silver_engine
from utils.logger import get_logger
 
logger = get_logger("gold.aggregator.discount_impact")
 
GOLD_TABLE = "gold.discount_impact"
 
 
def build(run_id: str) -> pd.DataFrame:
    """
    Category-level discount analysis from dummyjson products.
    Shows how much money customers save per unit vs paying full price.
    Useful for margin and pricing strategy decisions in the gold layer.
    """
    sql = text("""
        SELECT
            category,
            COUNT(*)                                                        AS total_products,
            ROUND(AVG(price)::NUMERIC, 2)                                   AS avg_full_price,
            ROUND(AVG(discount_percentage)::NUMERIC, 2)                     AS avg_discount_pct,
            ROUND(AVG(price * (1 - discount_percentage / 100))::NUMERIC, 2) AS avg_discounted_price,
            ROUND(AVG(price * discount_percentage / 100)::NUMERIC, 2)       AS total_savings_per_unit
        FROM silver.products_dummyjson
        WHERE discount_percentage IS NOT NULL
        GROUP BY category
        ORDER BY total_savings_per_unit DESC
    """)
 
    engine = get_silver_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
 
    df["_pipeline_run"] = run_id
    logger.info(f"Built {len(df)} rows for {GOLD_TABLE}")
    return df