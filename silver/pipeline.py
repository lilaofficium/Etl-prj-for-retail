import os
from datetime import datetime, timezone
from utils.logger import get_logger
from db.silver_connection import ensure_silver_schema
 
from silver.transformers import (
    fakestore_products,
    dummyjson_products,
    dummyjson_users,
    dummyjson_carts,
    jsonplaceholder_posts,
    joiner,
)
from silver.loader import upsert_to_silver, truncate_and_insert
 
logger = get_logger("silver_pipeline")
  
TRANSFORMERS = [
    (fakestore_products,     "silver.products_fakestore",  "product_id"),
    (dummyjson_products,     "silver.products_dummyjson",  "product_id"),
    (dummyjson_users,        "silver.users",               "user_id"),
    (dummyjson_carts,        "silver.carts",               "cart_id"),
    (jsonplaceholder_posts,  "silver.posts",               "post_id"),
]
 
 
def run_silver_pipeline() -> dict:
    run_id  = os.getenv("PIPELINE_RUN_ID", "silver-local")
    results = {}
  
    ensure_silver_schema()
  
    for transformer, table, pk in TRANSFORMERS:
        started_at = datetime.now(timezone.utc)
        try:
            logger.info(f"[{table}] Starting transform")
            df      = transformer.extract()
            df      = transformer.transform(df)
            rows    = upsert_to_silver(df, table, pk)
            results[table] = {"status": "success", "rows": rows}
            logger.info(f"[{table}] Done — {rows} rows upserted")
 
        except Exception as e:
            logger.error(f"[{table}] Failed: {e}")
            results[table] = {"status": "failed", "error": str(e)}
  
    try:
        logger.info("[silver.cart_user_summary] Building join")
        summary_df = joiner.build_cart_user_summary(run_id)
        rows       = truncate_and_insert(summary_df, "silver.cart_user_summary")
        results["silver.cart_user_summary"] = {"status": "success", "rows": rows}
        logger.info(f"[silver.cart_user_summary] Done — {rows} rows")
 
    except Exception as e:
        logger.error(f"[silver.cart_user_summary] Failed: {e}")
        results["silver.cart_user_summary"] = {"status": "failed", "error": str(e)}
 
    return results