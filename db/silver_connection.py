from sqlalchemy import create_engine, text
from config.settings import get_settings
from utils.logger import get_logger
 
logger   = get_logger("silver_db_connection")
settings = get_settings()
 
 
def get_silver_engine():
    engine = create_engine(
        settings.silver_postgres_url,
        pool_size=5,
        max_overflow=2,
        pool_pre_ping=True,
    )
    return engine
 
 
def ensure_silver_schema(migration_file: str = "db/migrations/silver_tables.sql") -> None: 
    engine = get_silver_engine()
 
    with open(migration_file, "r", encoding="utf-8") as f:
        sql_script = f.read()
 
    with engine.begin() as conn:
        conn.execute(text(sql_script))
 
    logger.info("Silver schema ensured.")
 
 
def test_silver_connection() -> bool:
    try:
        engine = get_silver_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Silver DB connected successfully")
        return True
    except Exception as e:
        logger.error(f"Silver DB connection failed: {e}")
        return False