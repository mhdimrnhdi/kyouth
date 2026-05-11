import sys
from pathlib import Path
from src.ingestor import ingest_all_mhtml

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None

    match command:
        case "ingest":
            ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)
        case _:
            print(f"Unknown command: {command}")
            print("Usage: python main.py ingest")


if __name__ == "__main__":
    main()
