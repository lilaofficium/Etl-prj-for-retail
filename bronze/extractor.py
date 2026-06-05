import requests
import pandas as pd 
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent)) 

from utils.logger import get_logger

logger = get_logger("Bronze_Extractor")


def get_api_data(url, params=None, headers=None, data_key=None):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()

    if data_key:
        data = data[data_key]

    return pd.json_normalize(data)


# def fetch_raw(source_name : str , url : str, data_key : str=None , retries :int =3 , timeout : int =10) -> list[dict]: 
#               try:
#                    for attempt in range(1, retries + 1):   
#                       logger.info(f"[{source_name}] Attempt {attempt} → {url}")
#                       response = requests.get(url, timeout=timeout)
#                       response.raise_for_status()  # Raise an exception for HTTP errors
#                       data = response.json()  
#                    return data if isinstance(data, list) else [data] 
#               except requests.exceptions.RequestException as e:
#                       logger.error(f"[{source_name}] Attempt {attempt} failed: {e}")
#                       if attempt == retries:
#                               logger.error(f"[{source_name}] All {retries} attempts failed. Skipping.")
#                               return []
#                       time.sleep(2 ** attempt)       