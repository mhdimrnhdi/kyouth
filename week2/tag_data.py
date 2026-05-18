import sys
import time
import sqlite3
import threading
import itertools
from prompt_model import prompt_model


def _spin(label: str, stop: threading.Event):
    # Prints an animated spinner until stop is set, then clears the line yeayyyy
    for char in itertools.cycle(r"|/-\\"):
        if stop.is_set():
            break
        print(f"\r{label} {char}", end="", flush=True)
        time.sleep(0.1)
    print("\r" + " " * (len(label) + 2) + "\r", end="", flush=True)

BATCH_SIZE = 5    # how many jobs to send to the LLM in one request
MAX_RETRIES = 3   # how many times to retry a failed batch before skipping it
RETRY_DELAY = 5   # seconds to wait between retries (keeps us within 15 RPM)
MODEL = "gm31" 


def tag_data(db_url: str):
    start = time.time()  # track total execution time
    total_tokens = 0     # accumulate token usage across all batches

    # connect to the database and fetch all rows that haven't been tagged yet
    try:
        conn = sqlite3.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT source_id, job_title, description FROM jobs WHERE tech_stack IS NULL OR TRIM(tech_stack) = ''"
        )
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        return

    # if everything is already tagged, exit early (idempotent re-run)
    if not rows:
        elapsed = round((time.time() - start) * 1000, 3)
        print("No data to tag")
        print(f"Total tokens used: 0, took {elapsed}ms")
        conn.close()
        return

    # split rows into batches of BATCH_SIZE
    batches = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
    job_counter = 0  # sequential number shown in output

    for batch_idx, batch in enumerate(batches):
        # build the prompt — one entry per job, including title for sparse descriptions
        prompt = (
            "Extract all specific named technologies from each job: programming languages, frameworks, libraries, databases, BI tools, cloud platforms, and dev tools "
            "(e.g. Python, Java, SQL, R, Node.js, PHP, React, Docker, PyTorch, TensorFlow, Tableau, Power BI, Excel, AWS, GCP, Git, Kafka, Spring Boot). "
            "Include everything explicitly mentioned AND infer standard tools commonly required for the role if not listed. "
            "Do NOT include soft skills or vague terms. "
            "Respond with ONLY one line per job, no extra text, no blank lines.\n"
            "Format: [source_id]: skill1, skill2, skill3\n\n"
        )
        for source_id, job_title, description in batch:
            desc = description or ""
            prompt += f"[{source_id}] ({job_title}): {desc}\n\n"

        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # show a spinner while waiting for the model response
                label = f"Batch {batch_idx + 1}/{len(batches)}, attempt {attempt}"
                stop = threading.Event()
                spinner = threading.Thread(target=_spin, args=(label, stop), daemon=True)
                spinner.start()

                # delegate to prompt_model — handles Google AI and Ollama routing
                text = prompt_model(MODEL, prompt)

                stop.set()
                spinner.join()

                # prompt_model returns an error string on failure, treat it as an exception
                if text.startswith("[Gemini Error]") or text.startswith("[Ollama Error]"):
                    raise ValueError(text)

                # estimate tokens at 4 per word (works for all models, incl. those without token counts)
                total_tokens += (len(prompt.split()) + len(text.split())) * 4

                # parse response into one line per job, ignoring blank lines
                lines = [l.strip() for l in text.strip().splitlines() if l.strip()]

                # if the model returned a different number of lines, the parse will be wrong — retry
                if len(lines) != len(batch):
                    raise ValueError("Mismatch between batch size and response")

                # extract tech_stack values and validate none are empty or N/A
                results = []
                for line in lines:
                    tech_stack = line.split(":", 1)[1].strip() if ":" in line else line.strip()
                    if not tech_stack or tech_stack.lower() == "n/a":
                        raise ValueError("Model returned empty skills for a job — retrying")
                    results.append(tech_stack)

                # write each result back to the database
                for tech_stack, (source_id, job_title, description) in zip(results, batch):
                    cursor.execute(
                        "UPDATE jobs SET tech_stack = ? WHERE source_id = ?",
                        (tech_stack, source_id)
                    )
                    job_counter += 1
                    print(f"Analyzed Job {job_counter}: {tech_stack}")

                conn.commit()  # save all writes for this batch at once
                success = True
                break

            except Exception as e:
                stop.set()
                spinner.join()
                print(f"[Batch {batch_idx}] Attempt {attempt} failed: {e}")
                if attempt < MAX_RETRIES:
                    wait = RETRY_DELAY * (2 ** (attempt - 1))  # 5s, 10s, 20s...
                    time.sleep(wait)

        if not success:
            print(f"[Batch {batch_idx}] Skipped after {MAX_RETRIES} failed attempts")

    conn.close()
    elapsed = round((time.time() - start) * 1000, 3)
    print(f"\nTotal tokens used: {total_tokens}, took {elapsed}ms")
    return total_tokens, elapsed  # bonus: return values for callers


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/resources/jobs_d1.db"
    tag_data(db_path)
