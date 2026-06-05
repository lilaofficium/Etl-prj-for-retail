import logging,os 
from datetime import datetime


def get_logger(name:str) -> logging.Logger :
    os.makedirs("logs",exist_ok=True)
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)

   # File Handeler - one log file per day
    fh=logging.FileHandler(f"logs/{datetime.now().date()}.log")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    ))

    logger.addHandler(fh)

    print(f"Logger {fh} created successfully")
    return logger