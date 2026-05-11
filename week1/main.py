import sys
from pathlib import Path
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR   = Path("data/3_gold")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None

    match command:
        case "ingest":
            ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)
        case "process":
            process_all_html(BRONZE_DIR, SILVER_DIR)
        case "load":
            load_all_jsons(SILVER_DIR, GOLD_DIR)
        case _:
            print(f"Unknown command: {command}")
            print("Usage: python main.py [ingest|process|load]")


if __name__ == "__main__":
    main()
