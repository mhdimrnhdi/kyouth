from pathlib import Path
import json
from bs4 import BeautifulSoup
from pydantic import BaseModel


class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str


def process_all_html(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🥈 Silver:...")

    if not input_dir.exists():
        print(f"⚠️ Input directory not found: {input_dir}")
        print("\n📊 Silver Summary:")
        print("Total: 0 | Processed: 0 | Skipped: 0")
        return

    files = sorted(input_dir.glob("*.html"))
    total = len(files)
    processed = 0
    skipped = 0

    if total == 0:
        print(f"⚠️ No .html files found in: {input_dir}")
        print("\n📊 Silver Summary:")
        print("Total: 0 | Processed: 0 | Skipped: 0")
        return

    for file in files:
        with open(file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Extract source_id from og:url meta tag
        og_url_tag = soup.find("meta", property="og:url")
        source_id = og_url_tag["content"].rstrip("/").split("/")[-1] if og_url_tag else None

        # Extract fields via data-automation attributes
        title_tag = soup.find(attrs={"data-automation": "job-detail-title"})
        company_tag = soup.find(attrs={"data-automation": "advertiser-name"})
        description_tag = soup.find(attrs={"data-automation": "jobAdDetails"})

        job_title = title_tag.get_text(separator=" ", strip=True) if title_tag else None
        company = company_tag.get_text(separator=" ", strip=True) if company_tag else None
        description = description_tag.get_text(separator=" ", strip=True) if description_tag else None

        # Warn and skip if any field is missing
        missing = False
        for field_name, value in [("source_id", source_id), ("job_title", job_title), ("company", company), ("description", description)]:
            if not value:
                print(f"⚠️ Missing {field_name} in: {file.name}")
                missing = True

        if missing:
            skipped += 1
            continue

        listing = JobListing(
            source_id=source_id,
            job_title=job_title,
            company=company,
            description=description,
        )

        out_file = output_dir / (file.stem + ".json")
        out_file.write_text(
            json.dumps(listing.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        processed += 1
        print(f"✅ Processed: {file.name}")

    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")
