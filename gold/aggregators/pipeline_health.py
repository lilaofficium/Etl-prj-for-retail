import pandas as pd
from sqlalchemy import text
from db.connection import get_engine
from utils.logger import get_logger
 
logger = get_logger("gold.aggregator.pipeline_health")
 
GOLD_TABLE = "gold.pipeline_health"
 
 
def build(run_id: str) -> pd.DataFrame:
    """
    Reads from bronze.pipeline_run_log to produce a run-level health summary.
    One row per pipeline run — useful for monitoring dashboards and alerting.
 
    Note: this reads from the BRONZE DB (not silver) because that's where
    pipeline_run_log lives. Gold is the only aggregator that crosses DB boundaries.
    """
    sql = text("""
        SELECT
            run_id,
            COUNT(*)                                        AS total_sources,
            COUNT(*) FILTER (WHERE status = 'success')     AS successful_sources,
            COUNT(*) FILTER (WHERE status = 'failed')      AS failed_sources,
            COALESCE(SUM(rows_inserted), 0)                AS total_rows_inserted,
            MIN(started_at)                                 AS started_at,
            MAX(finished_at)                                AS finished_at,
            ROUND(
                EXTRACT(EPOCH FROM (MAX(finished_at) - MIN(started_at)))::NUMERIC,
                2
            )                                              AS duration_seconds
        FROM bronze.pipeline_run_log
        GROUP BY run_id
        ORDER BY started_at DESC
    """)
 
    # Reads from bronze DB — pipeline_run_log lives there
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
 
    df["_pipeline_run"] = run_id
    logger.info(f"Built {len(df)} rows for {GOLD_TABLE}")
    return df