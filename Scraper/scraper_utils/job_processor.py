# system imports
import requests
from io import BytesIO
import certifi
import traceback
import warnings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urlunparse
from pathlib import Path
import json
import time

# project specific imports
from Scraper.models import Source, JobPosting, JobDetails # from models for database storage
from .pdf_processing import extract_text_normal, extract_text_ocr # for text extraction
from .summarizer import mock_llm_summarize #llm 
from .url_scraper import get_pdf_links_from_url #scrapes all pdf links from site

# global list, used to collect raw extracted text from pdf before saving to json 
extracted_text_data = []

# Suppresses annoying warnings from requests for unverified HTTPS certificates.
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# keywird list that is used to filter pdf
TEXT_KEYWORDS = ['recruitment', 'vacancy', 'invites application', 'job', 'posts available', 'engagement']
RETIRED_KEYWORDS = ['retired', 'superannuated', 'pensioner', 'ex-serviceman', 'former employee']

# Removes query fragments from URLs to avoid downloading duplicate PDFs.
def normalize_url(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))

# checks using keywords list if any relevant keyword is present in text
def is_job_related(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in TEXT_KEYWORDS)

def is_for_retired(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in RETIRED_KEYWORDS)

# I am calling functions from pdf_processing file for normal extraction of text or using OCR if short
def extract_text_from_pdf(pdf_bytes):
    text = extract_text_normal(pdf_bytes)
    if len(text.strip()) < 50:
        text = extract_text_ocr(pdf_bytes)
    return text

# helper function to log failed PDFs for retry later
def log_failed_pdf(pdf_url, error_type, message=""):
    data = {
        "pdf_url": pdf_url,
        "error_type": error_type,
        "message": message
    }
    failed_path = Path("failed_pdfs.json")
    with open(failed_path, "a", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")

# main worker function - takes pdf_url(link to pdf), source_url(link to where the pdf is found), session(used to handle retries and download pdf faster)
def process_pdf(pdf_url, source_url, session):
    try:
        pdf_url = pdf_url.replace("http://", "https://")  # Changes link to secure https://
        pdf_url = normalize_url(pdf_url) # Removes any query or extra fragments using normalize_url
        pdf_name = pdf_url.split("/")[-1] # Extracts just the file name like notice.pdf for saving or display
        
        # Tries to find if this source_url already exists in the Source table, if not creates new one
        source_name = urlparse(source_url).netloc or "Chandigarh Public Notices"
        source_obj, created = Source.objects.get_or_create(url=source_url, defaults={'name': source_name})
        if not created and source_obj.name != source_name:
            source_obj.name = source_name
            source_obj.save()

        # If the JobPosting table already has this PDF link, skip it
        if JobPosting.objects.filter(pdf_url=pdf_url).exists():
            print(f"[SKIPPED - Already processed] {pdf_name}")
            return "skipped"
        
        # Downloads the PDF using a GET request and uses a 10 second timeout to avoid hanging
        print(f"\n[DOWNLOADING] {pdf_url}")
        response = session.get(pdf_url, timeout=10, verify="/etc/ssl/certs/ca-certificates.crt") # checks whether the SSL certificate is trusted
        response.raise_for_status() # throws an error if server respond with 404/500 

        # converts the pdf content into bytes stream and passes it to text extractor
        pdf_bytes = BytesIO(response.content)
        text = extract_text_from_pdf(pdf_bytes.getvalue())

        # Checks if the text contains job-related keywords
        if not is_job_related(text):
            print(f"[SKIPPED - Not job related] {pdf_name}")
            return "skipped"

        # Checks if the text is meant for retired professionals
        if not is_for_retired(text):
            print(f"[SKIPPED - Not for retired people] {pdf_name}")
            return "skipped"
        
        # Adds this PDF's text content to the global list later which is written into json file
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

    except requests.exceptions.SSLError as ssl_error: # If the certificate is bad or SSL fails
        print(f"[SSL ERROR] {pdf_url}: {ssl_error}")
        log_failed_pdf(pdf_url, "ssl_error", str(ssl_error))
        return "error"
    except requests.exceptions.RequestException as e: # Network problems: timeout, connection refused
        print(f"[NETWORK ERROR] {pdf_url}: {e}")
        log_failed_pdf(pdf_url, "network_error", str(e))
        return "error"
    except Exception as e: 
        print(f"[PROCESSING ERROR] {pdf_url}: {e}")
        traceback.print_exc()
        log_failed_pdf(pdf_url, "processing_error", str(e))
        return "error"

# main controller function
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
    # multi threading
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
    
    # Save extracted text into a JSON file for teammate
    with open("extracted_texts.json", "w", encoding="utf-8") as f:
        json.dump(extracted_text_data, f, ensure_ascii=False, indent=4)

    print("[DONE] Extracted texts saved to extracted_texts.json")

    return results  # return at the very end, after saving JSON
