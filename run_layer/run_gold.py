import uuid
import os 
import sys 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
from gold.pipeline import run_gold_pipeline
 
os.environ["PIPELINE_RUN_ID"] = f"gold-{uuid.uuid4()}"
 
if __name__ == "__main__":
    results = run_gold_pipeline()
 
    print("\n===== GOLD PIPELINE SUMMARY =====")
    for table, info in results.items():
        status = info.get("status", "unknown")
        if status == "success":
            print(f"  success  {table:<40} {info.get('rows', 0)} rows loaded")
        else:
            print(f"  fail  {table:<40} FAILED — {info.get('error', 'unknown error')}")
    print("==================================\n")