import json
from pathlib import Path
import requests

from .job_processor import process_pdf  # Reuse existing logic

FAILED_LOG_FILE = Path("failed_pdfs.json")
RETRY_ATTEMPTS = 1  # can increase if needed

def retry_failed_pdfs():
    if not FAILED_LOG_FILE.exists():
        print("[INFO] No failed_pdfs.json file found. Nothing to retry.")
        return

    session = requests.Session()

    print("[RETRYING] Retrying PDFs that failed earlier...\n")
    
    updated_failures = []

    with open(FAILED_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                pdf_url = entry["pdf_url"]
                source_url = "manual-retry"  # dummy or actual source URL
                print(f"[RETRYING] {pdf_url}")
                
                result = process_pdf(pdf_url, source_url, session)

                if result == "downloaded":
                    print(f"[SUCCESS AFTER RETRY] {pdf_url}")
                else:
                    # if still fails (skipped or error), log again
                    updated_failures.append(entry)

            except Exception as e:
                print(f"[ERROR] Failed to retry this line: {e}")
                updated_failures.append(entry)

    # Overwrite the file with only the ones that failed again
    with open(FAILED_LOG_FILE, "w", encoding="utf-8") as f:
        for failure in updated_failures:
            json.dump(failure, f)
            f.write("\n")

    print(f"\n[RETRY DONE] Successfully reprocessed some PDFs. Remaining failures: {len(updated_failures)}")

if __name__ == "__main__":
    retry_failed_pdfs()
