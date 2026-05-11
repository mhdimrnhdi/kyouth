from pathlib import Path
import email
import quopri


def ingest_all_mhtml(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🥉 Bronze:...")

    if not input_dir.exists():
        print(f"⚠️ Source directory not found: {input_dir}")
        print("\n📊 Bronze Summary:")
        print("Total: 0 | Extracted: 0 | Failed: 0")
        return

    files = sorted(input_dir.glob("*.mhtml")) + sorted(input_dir.glob("*.mht"))
    total = len(files)
    extracted = 0
    failed = 0

    if total == 0:
        print(f"⚠️ No .mhtml files found in: {input_dir}")
        print("\n📊 Bronze Summary:")
        print("Total: 0 | Extracted: 0 | Failed: 0")
        return

    for file in files:
        html_content = None

        with open(file, "rb") as f:
            msg = email.message_from_binary_file(f)

        for part in msg.walk():
            if part.get_content_type() == "text/html":
                raw_payload = part.get_payload(decode=False)  # quoted-printable encoded string
                charset = part.get_content_charset() or "utf-8"
                decoded_bytes = quopri.decodestring(raw_payload.encode())
                html_content = decoded_bytes.decode(charset, errors="replace")
                break

        if html_content:
            out_file = output_dir / (file.stem + ".html")
            out_file.write_text(html_content, encoding="utf-8")
            extracted += 1
            print(f"✅ Extracted: {file.name}")
        else:
            failed += 1
            print(f"⚠️ No HTML content found in: {file.name}")

    print("\n📊 Bronze Summary:")
    print(f"Total: {total} | Extracted: {extracted} | Failed: {failed}")

