import sys
from pathlib import Path
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.profiler import run_data_profile

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR   = Path("data/3_gold")
DB_NAME    = "jobs.db"


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None

    match command:
        case "ingest":
            ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)
        case "process":
            process_all_html(BRONZE_DIR, SILVER_DIR)
        case "load":
            load_all_jsons(SILVER_DIR, GOLD_DIR)
        case "profile":
            run_data_profile(GOLD_DIR / DB_NAME)
        case "all":
            ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)
            process_all_html(BRONZE_DIR, SILVER_DIR)
            load_all_jsons(SILVER_DIR, GOLD_DIR)
            run_data_profile(GOLD_DIR / DB_NAME)
        case _:
            print("Usage: python main.py [ingest|process|load|profile|all]")


if __name__ == "__main__":
    main()
