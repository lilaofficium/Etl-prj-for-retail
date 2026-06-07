import pandas as pd
from sqlalchemy import text
from db.connection import get_engine
from utils.logger import get_logger
 
logger = get_logger("silver.transformers.dummyjson_users")
 
BRONZE_TABLE = "bronze.dummyjson_users"
SILVER_TABLE = "silver.users"
PRIMARY_KEY  = "user_id"
 
 
def extract() -> pd.DataFrame:
    sql = text(f"""
        SELECT DISTINCT ON (id)
            id, "firstName", "lastName", "maidenName",
            age, gender, email, phone, username,
            "birthDate", image, "bloodGroup",
            height, weight, "eyeColor",
            ip, "macAddress", university,
            ein, ssn, role,
            _source, _ingested_at, _pipeline_run
        FROM {BRONZE_TABLE}
        ORDER BY id, _ingested_at DESC
    """)
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
    logger.info(f"Extracted {len(df)} rows from {BRONZE_TABLE}")
    return df
 
 
def transform(df: pd.DataFrame) -> pd.DataFrame: 
    df = df.rename(columns={
        "id"          : "user_id",
        "firstName"   : "first_name",
        "lastName"    : "last_name",
        "maidenName"  : "maiden_name",
        "birthDate"   : "birth_date",
        "image"       : "image_url",
        "bloodGroup"  : "blood_group",
        "eyeColor"    : "eye_color",
        "ip"          : "ip_address",
        "macAddress"  : "mac_address",
    })
  
    df["user_id"]      = pd.to_numeric(df["user_id"], errors="coerce").astype("Int64")
    df["age"]          = pd.to_numeric(df["age"],     errors="coerce").astype("Int64")
    df["height"]       = pd.to_numeric(df["height"],  errors="coerce")
    df["weight"]       = pd.to_numeric(df["weight"],  errors="coerce")
    df["birth_date"]   = pd.to_datetime(df["birth_date"], errors="coerce").dt.date
    df["_ingested_at"] = pd.to_datetime(df["_ingested_at"], utc=True, errors="coerce")
  
    before = len(df)
    df = df.dropna(subset=["user_id", "email"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped} rows with null user_id / email")
  
    df = df.drop(columns=["image_url"], errors="ignore")
   
  
    df = df[[
        "user_id", "first_name", "last_name", "maiden_name",
        "age", "gender", "email", "phone", "username",
        "birth_date", "blood_group", "height", "weight", "eye_color",
        "ip_address", "mac_address", "university",
        "ein", "ssn", "role",
        "_source", "_ingested_at", "_pipeline_run"
    ]]
 
    logger.info(f"Transformed {len(df)} rows for {SILVER_TABLE}")
    return df