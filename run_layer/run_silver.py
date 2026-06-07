import uuid
import os 
import sys 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
from silver.pipeline import run_silver_pipeline
  
os.environ["PIPELINE_RUN_ID"] = f"silver-{uuid.uuid4()}"
 
if __name__ == "__main__":
    results = run_silver_pipeline()
 
    print("\n===== SILVER PIPELINE SUMMARY =====")
    for table, info in results.items():
        status = info.get("status", "unknown")
        if status == "success":
            print(f"  suceed  {table:<40} {info.get('rows', 0)} rows upserted")
        else:
            print(f"  failed  {table:<40} FAILED — {info.get('error', 'unknown error')}")
    print("====================================\n")
 