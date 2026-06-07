import uuid
import os
import sys
 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bronze.pipeline import run_bronze_pipeline
from silver.pipeline import run_silver_pipeline
from gold.pipeline import run_gold_pipeline


def print_summary(layer_name, results):
    print(f"\n===== {layer_name.upper()} PIPELINE SUMMARY =====")

    for item, info in results.items():
        status = info.get("status", "unknown")

        if status == "success":
            rows = info.get("rows", 0)

            if layer_name.lower() == "silver":
                print(f" success {item:<40} {rows} rows upserted")
            else:
                print(f" success {item:<40} {rows} rows loaded")
        else:
            print(
                f"  failed {item:<40} FAILED — "
                f"{info.get('error', 'unknown error')}"
            )

    print("=" * 50)


def main(): 
    os.environ["PIPELINE_RUN_ID"] = str(uuid.uuid4())

    print("\nStarting Bronze Pipeline...")
    bronze_results = run_bronze_pipeline()
    print_summary("Bronze", bronze_results)

    print("\nStarting Silver Pipeline...")
    silver_results = run_silver_pipeline()
    print_summary("Silver", silver_results)

    print("\nStarting Gold Pipeline...")
    gold_results = run_gold_pipeline()
    print_summary("Gold", gold_results)

    print("\nAll pipelines completed.")


if __name__ == "__main__":
    main()