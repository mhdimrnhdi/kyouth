from pathlib import Path
import json
import sqlite3


def load_all_jsons(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🥇 Gold:...")

    if not input_dir.exists():
        print(f"⚠️ Input directory not found: {input_dir}")
        print("\n📊 Gold Summary:")
        print("Total: 0 | Inserted: 0 | Skipped: 0")
        return

    files = sorted(input_dir.glob("*.json"))
    total = len(files)
    inserted = 0
    skipped = 0

    if total == 0:
        print(f"⚠️ No .json files found in: {input_dir}")
        print("\n📊 Gold Summary:")
        print("Total: 0 | Inserted: 0 | Skipped: 0")
        return

    db_path = output_dir / "jobs.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            source_id   TEXT PRIMARY KEY,
            job_title   TEXT,
            company     TEXT,
            description TEXT,
            tech_stack  TEXT
        )
        """
    )
    conn.commit()

    for file in files:
        with open(file, encoding="utf-8") as f:
            data = json.load(f)

        cursor.execute(
            """
            INSERT OR IGNORE INTO jobs (source_id, job_title, company, description, tech_stack)
            VALUES (?, ?, ?, ?, ?)
            """,
            (data["source_id"], data["job_title"], data["company"], data["description"], None),
        )
        conn.commit()

        if cursor.rowcount == 1:
            inserted += 1
            print(f"✅ Inserted: {file.name}")
        else:
            skipped += 1
            print(f"⏭️ Skipped (duplicate): {file.name}")

    conn.close()

    print("\n📊 Gold Summary:")
    print(f"Total: {total} | Inserted: {inserted} | Skipped: {skipped}")
