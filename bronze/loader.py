from utils.logger import get_logger 
from bronze.insert_query import  insert_dataframe,ensure_table_exists,log_pipeline_run
import pandas as pd
from datetime import datetime, timezone 

logger   = get_logger("bronze.loader") 

TABLE_MAP = {
    "fakestore_products"    : "bronze.fakestore_products",
    "dummyjson_products"    : "bronze.dummyjson_products",
    "dummyjson_users"       : "bronze.dummyjson_users",
    "dummyjson_carts"       : "bronze.dummyjson_carts",
    "jsonplaceholder_posts" : "bronze.jsonplaceholder_posts",
}
 
def save_to_bronze(df: pd.DataFrame,source_name: str, run_id: str) -> int:

    table = TABLE_MAP.get(source_name)
    if not table:
        raise ValueError(f"No table mapped for source: {source_name}")
    else : 
        # df=rename_column_map(df,source_name)  
        if ensure_table_exists(table)==True : 
          insert_dataframe(df, table)   
        else :
            print('craeted ')
    return len(df)
 
 
def add_metadata( df: pd.DataFrame, source_name: str, run_id: str = "parquet") -> list[dict]:
    ingestion_time = datetime.now(timezone.utc).isoformat()

    df = df.copy()
    df["_source"] = source_name
    df["_ingested_at"] = ingestion_time
    df["_pipeline_run"] = run_id  
    df["_batch_id"] = run_id  
    df.columns
    return df



# def insert_dataframe(df: pd.DataFrame, table: str = "bronze.fakestore_products") -> int:
#     if df.empty:
#         print("[insert_dataframe] DataFrame is empty, skipping insert.")
#         return 0

#     try:
#         df = df.copy()

#         #  this will be diffrent according to table start 
#         df["rating"] = df.apply(
#             lambda row: json.dumps({
#                 "rate": row["rating.rate"],
#                 "count": row["rating.count"]
#             }), axis=1
#         )

#         # Exact DB columns (excluding _batch_id — serial4, auto-generated)
#         insert_cols = ["id", "title", "price", "description", "category",
#                        "image", "rating", "_source", "_ingested_at", "_pipeline_run"]

#         # Cast to match DB types exactly
#         df["id"]            = df["id"].astype(int)           # int4
#         df["price"]         = df["price"].astype(str)        # text
#         df["_ingested_at"]  = pd.to_datetime(df["_ingested_at"], utc=True)  # timestamptz
#         df["_pipeline_run"] = df["_pipeline_run"].astype(str)  # varchar(50)
#         df["_source"]       = df["_source"].astype(str)        # varchar(100)

#         records = (
#             df[insert_cols]
#             .where(pd.notna(df[insert_cols]), None)
#             .to_dict(orient="records")
#         )

#         engine = get_engine()

#         sql = text("""
#             INSERT INTO bronze.fakestore_products (
#                 id, title, price, description, category,
#                 image, rating, _source, _ingested_at, _pipeline_run
#             ) VALUES (
#                 :id, :title, :price, :description, :category,
#                 :image, :rating, :_source, :_ingested_at, :_pipeline_run
#             )
#         """)
#                #  this will be diffrent according to table start  i want this code in switch statemant in diffrent function so that i can return on the basic of table name
#         with engine.begin() as conn:
#             conn.execute(sql, records)

#         print(f"[insert_dataframe] Inserted {len(records)} rows into {table}.")
#         return len(records)

#     except Exception as e:
#         print(f"[insert_dataframe] Failed to insert into {table}: {e}")
#         raise

# def save_to_bronze(records:list[dict],source_name: str,format:str="parquet") -> str :
#       date_partition =datetime.now().date().strftime("%Y-%m-%d")
#       folder=f"storage/bronze/{source_name}/date={date_partition}" 
#       os.makedirs(folder,exist_ok=True)

#       df= pd.DataFrame(records)

#       if format == "parquet" :
#             file_path = f"{folder}/data_{datetime.now().strftime('%H%M%S')}.parquet"
#             df.to_parquet(file_path,index=False)
#       elif format == "json" :
#             file_path = f"{folder}/data_{datetime.now().strftime('%H%M%S')}.json"
#             with open(file_path,"w") as f :
#                   json.dump(records,f,indent=2,default=str)
#       logger.info(f"[{source_name}] Saved {len(records)} records to {file_path}")
#       return file_path