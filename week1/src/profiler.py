from pathlib import Path
import sqlite3


def run_data_profile(db_path):
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT
            SUM(CASE WHEN job_title IS NULL OR job_title = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN company IS NULL OR company = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END)
        FROM jobs
        """
    )
    null_title, null_company, null_desc = cursor.fetchone()

    cursor.execute("SELECT AVG(LENGTH(description)) FROM jobs")
    avg_len = int(cursor.fetchone()[0] or 0)

    cursor.execute(
        """
        SELECT LENGTH(description), source_id, job_title
        FROM jobs
        ORDER BY LENGTH(description) ASC
        LIMIT 1
        """
    )
    shortest_len, shortest_id, shortest_title = cursor.fetchone()

    cursor.execute(
        """
        SELECT LENGTH(description), source_id, job_title
        FROM jobs
        ORDER BY LENGTH(description) DESC
        LIMIT 1
        """
    )
    longest_len, longest_id, longest_title = cursor.fetchone()

    conn.close()

    print("--- 🔍 DATA QUALITY REPORT ---")
    print(f"📈 Total Records: {total}")
    print(f"❓ Missing Values -> job_title: {null_title}, company: {null_company}, description: {null_desc}")
    print(f"📝 Avg Description Length: {avg_len} chars")
    print(f"⚠️  Shortest Description: {shortest_len} chars")
    print(f"   ↳ source_id: {shortest_id} | job_title: {shortest_title}")
    print(f"🚨 Longest Description: {longest_len} chars")
    print(f"   ↳ source_id: {longest_id} | job_title: {longest_title}")
