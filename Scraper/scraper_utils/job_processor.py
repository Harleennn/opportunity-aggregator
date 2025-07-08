import requests
from io import BytesIO
import certifi
import traceback
import warnings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urlunparse

from Scraper.models import Source, JobPosting, JobDetails
from .pdf_processing import extract_text_normal, extract_text_ocr
from .summarizer import mock_llm_summarize
from .url_scraper import get_pdf_links_from_url
extracted_text_data = []
import json


warnings.filterwarnings("ignore", message="Unverified HTTPS request")

TEXT_KEYWORDS = ['recruitment', 'vacancy', 'invites application', 'job', 'posts available', 'engagement']
RETIRED_KEYWORDS = ['retired', 'superannuated', 'pensioner', 'ex-serviceman', 'former employee']


def normalize_url(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))


def is_job_related(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in TEXT_KEYWORDS)


def is_for_retired(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in RETIRED_KEYWORDS)


def extract_text_from_pdf(pdf_bytes):
    text = extract_text_normal(pdf_bytes)
    if len(text.strip()) < 50:
        text = extract_text_ocr(pdf_bytes)
    return text




def process_pdf(pdf_url, source_url, session):
    try:
        pdf_url = pdf_url.replace("http://", "https://")
        pdf_url = normalize_url(pdf_url)
        pdf_name = pdf_url.split("/")[-1]

        source_name = urlparse(source_url).netloc or "Chandigarh Public Notices"
        source_obj, created = Source.objects.get_or_create(url=source_url, defaults={'name': source_name})
        if not created and source_obj.name != source_name:
            source_obj.name = source_name
            source_obj.save()
 

        if JobPosting.objects.filter(pdf_url=pdf_url).exists():
            print(f"[SKIPPED - Already processed] {pdf_name}")
            return "skipped"

        print(f"\n[DOWNLOADING] {pdf_url}")
        response = session.get(pdf_url, timeout=10, verify="/etc/ssl/certs/ca-certificates.crt")
        response.raise_for_status()

        pdf_bytes = BytesIO(response.content)
        text = extract_text_from_pdf(pdf_bytes.getvalue())

        if not is_job_related(text):
            print(f"[SKIPPED - Not job related] {pdf_name}")
            return "skipped"

        if not is_for_retired(text):
            print(f"[SKIPPED - Not for retired people] {pdf_name}")
            return "skipped"
        # Add this after filtering checks
        extracted_text_data.append({
            "file_name": pdf_name,
            "text": text
        })

        # Summarize using LLM
        posting_data, job_details_data = mock_llm_summarize(text, pdf_name=pdf_name)

        # Save to DB
        job_posting = JobPosting.objects.create(
            source=source_obj,
            pdf_name=pdf_name,
            pdf_url=pdf_url,
            age_limit=posting_data.get("age_limit"),
            application_deadline=posting_data.get("application_deadline"),
            pay_scale=posting_data.get("pay_scale"),
            employment_type=posting_data.get("employment_type")
        )

        JobDetails.objects.create(
            posting=job_posting,
            title=job_details_data.get("title"),
            eligibility=job_details_data.get("eligibility"),
            minimum_qualification=job_details_data.get("minimum_qualification"),
            overall_skill=job_details_data.get("overall_skill"),
        )

        print(f"[SAVED] {pdf_name}")
        return "downloaded"

    except requests.exceptions.SSLError as ssl_error:
        print(f"[SSL ERROR] {pdf_url}: {ssl_error}")
        return "error"
    except requests.exceptions.RequestException as e:
        print(f"[NETWORK ERROR] {pdf_url}: {e}")
        return "error"
    except Exception as e:
        print(f"[PROCESSING ERROR] {pdf_url}: {e}")
        traceback.print_exc()
        return "error"


def process_all_pdfs(source_url):
    print(f"\n[STARTING] Scrape from: {source_url}")
    pdf_links = get_pdf_links_from_url(source_url)
    print(f"[FOUND] {len(pdf_links)} PDF links.")

    if not pdf_links:
        print("[INFO] No PDF links found. Exiting.")
        return []

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    results = []
    downloaded, skipped, errors = 0, 0, 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_pdf = {
            executor.submit(process_pdf, pdf_url, source_url, session): pdf_url
            for pdf_url in pdf_links
        }

        for future in as_completed(future_to_pdf):
            result = future.result()
            results.append(result)
            if result == "downloaded":
                downloaded += 1
            elif result == "skipped":
                skipped += 1
            else:
                errors += 1

    print(f"\n[SUMMARY] Total PDFs: {len(pdf_links)}, Downloaded: {downloaded}, Skipped: {skipped}, Errors: {errors}")
    
     #  Save extracted text into a JSON file for teammate
    with open("extracted_texts.json", "w", encoding="utf-8") as f:
        json.dump(extracted_text_data, f, ensure_ascii=False, indent=4)

    print("[DONE] Extracted texts saved to extracted_texts.json")

    return results  #  return at the very end, after saving JSON

