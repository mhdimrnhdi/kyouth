Week 1: Data Pipeline

## Project Description

A local ETL pipeline that processes job listings scraped from Jobstreet Malaysia. Raw `.mhtml` web archive files are extracted, cleaned, and loaded into a structured SQLite database (`jobs.db`).

```
[0_source .mhtml] -> [1_bronze .html] -> [2_silver .json] -> [3_gold jobs.db]
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher (uses `match/case` syntax)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — fast Python package manager

### Install `uv`

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Dependencies

```bash
cd week1
uv sync
```

> This reads `pyproject.toml` and installs all dependencies into a local `.venv` automatically.

---

## Usage

All commands are run from the `week1/` directory:

```bash
cd week1
```

| Command | What it does |
|---|---|
| `uv run python main.py ingest` | Extract `.mhtml` → `.html` into `data/1_bronze/` |
| `uv run python main.py process` | Clean `.html` → `.json` into `data/2_silver/` |
| `uv run python main.py load` | Load `.json` → `jobs.db` into `data/3_gold/` |
| `uv run python main.py profile` | Print data quality report from `jobs.db` |
| `uv run python main.py all` | Run all four steps in order |

### Expected output (full run)

```
🥉 Bronze:...
✅ Extracted: AI Engineer Job in Kuala Lumpur - Jobstreet.mhtml
...
📊 Bronze Summary:
Total: 100 | Extracted: 100 | Failed: 0

🥈 Silver:...
✅ Processed: AI Engineer Job in Kuala Lumpur - Jobstreet.html
...
📊 Silver Summary:
Total: 100 | Processed: 84 | Skipped: 16

🥇 Gold:...
✅ Inserted: AI Engineer Job in Kuala Lumpur - Jobstreet.json
...
📊 Gold Summary:
Total: 84 | Inserted: 84 | Skipped: 0

--- 🔍 DATA QUALITY REPORT ---
📈 Total Records: 84
❓ Missing Values -> job_title: 0, company: 0, description: 0
📝 Avg Description Length: 2654 chars
⚠️  Shortest Description: 32 chars
   ↳ source_id: 91647393 | job_title: Software Engineer
🚨 Longest Description: 6781 chars
   ↳ source_id: 91731564 | job_title: Automation Engineer
```

---

## Technical Reflections

### Module 1: The Extractor (Medallion & Lakehouses)
Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?
- **Answer**: Keeping raw HTML in `1_bronze/` means if the processor has a bug, you fix the code and re-run; no re-downloading needed. Raw data is treated as fixed, just like a data lake. You can also open any `.html` file and inspect exactly what the parser saw, which makes debugging straightforward.

### Module 2: Treatment Plant (ETL vs ELT & Scale)
Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?
- **Answer**: Cloud warehouses like BigQuery have massive built-in compute, so it's faster to load raw data first and transform it using SQL inside the warehouse (ELT). Processing files one at a time is fine at 100 files but breaks down at millions. Distributed systems split the data across machines and process chunks in parallel, cutting hours down to minutes.

### Module 3: The Blueprint & The Vault (Storage & Contracts)
What should happen if an important field like `job_title` disappears? Why fail early instead of silently inserting nulls into DB? How does `INSERT OR IGNORE` help prevent duplicate records?
- **Answer**: The processor skips any record with a missing field and warns loudly — nulls silently inserted today become broken queries or dashboards later. Failing early at the boundary (enforced via Pydantic) keeps bad data out entirely. `INSERT OR IGNORE` uses `source_id` as a primary key, so re-running the pipeline never creates duplicate rows.

### Module 4: The QA Inspector & Orchestrator (Orchestration & DAGs)
What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?
- **Answer**: If `processor.py` crashes, `main.py all` stops completely with no record of what succeeded. You have to re-run everything manually. Tools like Airflow model each step as a node in a Directed Acrylic Graph (DAG). On failure it retries only the failed step, logs what happened, and can alert you automatically. It also handles scheduling and dependencies, things the `main.py` can't do.
