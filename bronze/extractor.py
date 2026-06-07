import time
import requests
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import get_settings
from utils.logger import get_logger

logger   = get_logger("bronze.extractor")
settings = get_settings()


def get_api_data(url: str, params=None, headers=None, data_key=None) -> pd.DataFrame:
    
    first_page = _fetch_with_retry(url, params=params, headers=headers)
 
    if not isinstance(first_page, dict) or "total" not in first_page: 
        data = first_page if isinstance(first_page, list) else first_page.get(data_key, [])
        logger.info(f"[{url}] Non-paginated — {len(data)} records fetched")
        return pd.json_normalize(data)

    total     = first_page["total"]
    page_data = first_page.get(data_key, []) if data_key else first_page
    limit     = len(page_data)          # use actual page size returned by the API
    all_rows  = list(page_data)

    logger.info(f"[{url}] Paginated — total={total}, page_size={limit}")
 
    skip = limit
    while skip < total:
        page_params = dict(params or {})
        page_params["limit"] = limit
        page_params["skip"]  = skip

        page = _fetch_with_retry(url, params=page_params, headers=headers)
        chunk = page.get(data_key, []) if data_key else page
        all_rows.extend(chunk)
        logger.info(f"[{url}] Fetched {len(all_rows)}/{total} records")
        skip += limit

    return pd.json_normalize(all_rows)


def _fetch_with_retry(url: str, params=None, headers=None) -> dict | list:
    
    last_error = None

    for attempt in range(1, settings.api_retry_count + 1):
        try:
            logger.info(f"Attempt {attempt}/{settings.api_retry_count} → {url}")
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=settings.api_timeout,  
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            last_error = e
            logger.warning(f"Attempt {attempt} failed: {e}")

            if attempt < settings.api_retry_count:
                wait = settings.api_retry_backoff ** attempt   # exponential: 2s, 4s, 8s...
                logger.info(f"Retrying in {wait}s...")
                time.sleep(wait)
 
    raise RuntimeError(
        f"All {settings.api_retry_count} attempts failed for {url}: {last_error}"
    )
