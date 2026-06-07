import pandas as pd
from sqlalchemy import text
from db.connection import get_engine
from utils.logger import get_logger
 
logger = get_logger("silver.transformer.dummyjson_products")
 
BRONZE_TABLE = "bronze.dummyjson_products"
SILVER_TABLE = "silver.products_dummyjson"
PRIMARY_KEY  = "product_id"
 
 
def extract() -> pd.DataFrame:
    sql = text(f"""
        SELECT DISTINCT ON (id)
            id, title, description, category, price,
            "discountPercentage", rating, stock,
            brand, sku, weight,
            "warrantyInformation", "shippingInformation",
            "availabilityStatus", "returnPolicy",
            "minimumOrderQuantity", thumbnail,
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
        "id"                   : "product_id",
        "discountPercentage"   : "discount_percentage",
        "warrantyInformation"  : "warranty_information",
        "shippingInformation"  : "shipping_information",
        "availabilityStatus"   : "availability_status",
        "returnPolicy"         : "return_policy",
        "minimumOrderQuantity" : "minimum_order_quantity",
        "thumbnail"            : "thumbnail_url",
    })
  
    df["product_id"]            = pd.to_numeric(df["product_id"],            errors="coerce").astype("Int64")
    df["price"]                 = pd.to_numeric(df["price"],                 errors="coerce")
    df["discount_percentage"]   = pd.to_numeric(df["discount_percentage"],   errors="coerce")
    df["rating"]                = pd.to_numeric(df["rating"],                errors="coerce")
    df["stock"]                 = pd.to_numeric(df["stock"],                 errors="coerce").astype("Int64")
    df["weight"]                = pd.to_numeric(df["weight"],                errors="coerce")
    df["minimum_order_quantity"] = pd.to_numeric(df["minimum_order_quantity"], errors="coerce").astype("Int64")
    df["_ingested_at"]          = pd.to_datetime(df["_ingested_at"], utc=True, errors="coerce")
  
    before = len(df)
    df = df.dropna(subset=["product_id", "title", "price"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped} rows with null product_id / title / price")
  
    df = df[[
        "product_id", "title", "description", "category", "price",
        "discount_percentage", "rating", "stock",
        "brand", "sku", "weight",
        "warranty_information", "shipping_information",
        "availability_status", "return_policy",
        "minimum_order_quantity", "thumbnail_url",
        "_source", "_ingested_at", "_pipeline_run"
    ]]
 
    logger.info(f"Transformed {len(df)} rows for {SILVER_TABLE}")
    return df