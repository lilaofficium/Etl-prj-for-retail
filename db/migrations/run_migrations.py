from db.connection import get_connection
from utils.logger import get_logger
import os

logger = get_logger("migrations")

def run_migrations():
    """
    Run bronze_tables.sql against PostgreSQL.
    Safe to run multiple times — uses CREATE IF NOT EXISTS.
    """
    sql_path = os.path.join(
        os.path.dirname(__file__), "bronze_tables.sql"
    )
    with open(sql_path, "r") as f:
        sql = f.read()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    logger.info("✅ Bronze tables created / verified successfully")

if __name__ == "__main__":
    run_migrations()