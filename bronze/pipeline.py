import yaml
import os
from datetime import datetime, timezone
from bronze.extractor import get_api_data 
from bronze.loader import add_metadata, save_to_bronze, log_pipeline_run
from utils.logger import get_logger

logger = get_logger("bronze_pipeline")

def run_bronze_pipeline(config_path: str = "config/sources.yaml") -> dict:
    with open(config_path) as f:
        config = yaml.safe_load(f)

    run_id  = os.getenv("PIPELINE_RUN_ID", "local")   
    results = {}

    for source_name, cfg in config["sources"].items():
        started_at = datetime.now(timezone.utc)

        try:                                       
            logger.info(f"[{source_name}] Starting ingestion")

            raw_records = get_api_data(
                cfg["url"],
                params=None,
                data_key=cfg.get("data_key")
            )

            enriched = add_metadata(raw_records, source_name, run_id)
            rows     = save_to_bronze(enriched, source_name, run_id)
            finished_at = datetime.now(timezone.utc)

            log_pipeline_run(
                run_id=run_id,
                source_name=source_name,
                status="success",
                rows_inserted=rows,
                started_at=started_at,
                finished_at=finished_at,
            )

            results[source_name] = {"status": "success", "rows": rows}  
            logger.info(f"[{source_name}] Done — {rows} rows inserted")

        except Exception as e:
            finished_at = datetime.now(timezone.utc)
            logger.error(f"[{source_name}] Failed: {e}")

            log_pipeline_run(
                run_id=run_id,
                source_name=source_name,
                status="failed",
                rows_inserted=0,
                error_message=str(e),
                started_at=started_at,
                finished_at=finished_at,
            )

            results[source_name] = {"status": "failed", "error": str(e)}  

    return results
 