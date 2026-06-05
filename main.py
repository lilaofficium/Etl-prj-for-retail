import uuid ,os 
from bronze.pipeline import run_bronze_pipeline

os.environ["PIPELINE_RUN_ID"] = str(uuid.uuid4())

if __name__ == "__main__":
    results = run_bronze_pipeline()
    print("\n===== BRONZE PIPELINE SUMMARY =====")
    for source,info in results.items() :
        print(f"taskdone") 