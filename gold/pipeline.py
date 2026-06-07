import os
from datetime import datetime, timezone
from utils.logger import get_logger
from db.gold_connection import ensure_gold_schema
from gold.loader import load_to_gold
 
from gold.aggregators import (
    sales_by_category,
    top_spenders,
    product_performance,
    discount_impact,
    user_demographics,
    post_activity,
    pipeline_health,
)
 
logger = get_logger("gold_pipeline")
 
# Registry: (aggregator_module, gold_table)
# To add a new KPI: write the aggregator, register it here. That's it.
AGGREGATORS = [
    (sales_by_category,   "gold.sales_by_category"),
    (top_spenders,        "gold.top_spenders"),
    (product_performance, "gold.product_performance"),
    (discount_impact,     "gold.discount_impact"),
    (user_demographics,   "gold.user_demographics"),
    (post_activity,       "gold.post_activity"),
    (pipeline_health,     "gold.pipeline_health"),
]
 
 
def run_gold_pipeline() -> dict:
    run_id  = os.getenv("PIPELINE_RUN_ID", "gold-local")
    results = {}
 
    # Ensure all gold tables exist before writing
    ensure_gold_schema()
 
    for aggregator, table in AGGREGATORS:
        try:
            logger.info(f"[{table}] Building aggregation")
            df   = aggregator.build(run_id)
            rows = load_to_gold(df, table)
            results[table] = {"status": "success", "rows": rows}
            logger.info(f"[{table}] Done — {rows} rows loaded")
 
        except Exception as e:
            logger.error(f"[{table}] Failed: {e}")
            results[table] = {"status": "failed", "error": str(e)}
 
    return results