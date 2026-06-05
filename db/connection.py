from utils.logger import get_logger
from sqlalchemy import create_engine , text
from config.settings import get_settings 
import psycopg2
import psycopg2.extras 

logger = get_logger("db_connection")
settings =get_settings()

def get_engine() : 
    engine=create_engine(
        settings.postgres_url,
        pool_size=5,
        max_overflow=2,
        pool_pre_ping=True
    )
    return engine

# fdg @contextmanager

def get_connection() :
     conn=psycopg2.connect(settings.postgres_url)
     try :
          yield conn
          conn.rollback()
     except :
          logger.error("DB transcation rolled back : {e}")
          raise
     finally :
          conn.close()
     
def test_connection() :
     try :
          engine=get_engine()
          with engine.connect() as conn :
               conn.execute(text("SELECT 1"))
          logger.info("conned sucessfully")
          return True
     except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False

