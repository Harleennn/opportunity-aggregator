import requests
import fitz  # PyMuPDF
import pytesseract
from bs4 import BeautifulSoup
from io import BytesIO
from pdf2image import convert_from_bytes
from .models import JobSummary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time
import certifi
import warnings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ignore SSL warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Keyword filters
TEXT_KEYWORDS = ['recruitment', 'vacancy', 'invites application', 'job', 'posts available', 'engagement']
RETIRED_KEYWORDS = ['retired', 'superannuated', 'pensioner', 'ex-serviceman', 'former employee']
REQUIRED_YEAR = ['2023', '2024', '2025']  # Optional

# Mock LLM summarizer
def mock_llm_summarize(text, pdf_name=None):
    summary = {
        "title": "Test Job",
        "eligibility": "Any graduate",
        "minimum_qualification": "None",
        "age_limit": "18-35",
        "application_deadline": "31 July 2025",
        "pay_scale": "20,000 INR",
        "employment_type": "Contract",
        "overall_skill": "Typing, Communication"
    }
    if pdf_name:
        summary["title"] += f" - {pdf_name}"
    return summary

# Headless Chrome
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)

# Extract PDF links from webpage
def get_pdf_links_from_url(url):
    driver = get_driver()
    driver.get(url)
    time.sleep(5)

    anchors = driver.find_elements(By.TAG_NAME, 'a')
    links = []
    for link in anchors:
        href = link.get_attribute("href")
        if href and href.endswith(".pdf"):
            full_href = urljoin(url, href)
            print(f"[DEBUG] Found PDF link: {full_href}")
            links.append(full_href)

    driver.quit()
    return list(set(links))  # Remove duplicates

# Extract text using PyMuPDF
def extract_text_normal(pdf_bytes):
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Fallback OCR using pytesseract
def extract_text_ocr(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text

# Worker function to process each PDF
def process_pdf(pdf_url, source_url, session):
    try:
        if pdf_url.startswith("http://"):
            pdf_url = pdf_url.replace("http://", "https://")

        pdf_name = pdf_url.split("/")[-1]

        if JobSummary.objects.filter(pdf_name=pdf_name, source_url=source_url).exists():
            print(f"Already processed: {pdf_name}")
            return "skipped"

        print(f"\nDownloading: {pdf_url}")
        response = session.get(pdf_url, timeout=10, verify=certifi.where())
        response.raise_for_status()

        pdf_bytes = BytesIO(response.content)

        text = extract_text_normal(pdf_bytes.getvalue())
        if len(text.strip()) < 50:
            text = extract_text_ocr(pdf_bytes.getvalue())

        text_lower = text.lower()

        if not any(kw in text_lower for kw in TEXT_KEYWORDS):
            print(f"Skipped (not job related): {pdf_name}")
            return "skipped"

        if not any(kw in text_lower for kw in RETIRED_KEYWORDS):
            print(f"Skipped (not for retired people): {pdf_name}")
            return "skipped"

        summary_data = mock_llm_summarize(text, pdf_name=pdf_name)

        JobSummary.objects.create(
            source_url=source_url,
            pdf_name=pdf_name,
            title=summary_data.get("title"),
            eligibility=summary_data.get("eligibility"),
            minimum_qualification=summary_data.get("minimum_qualification"),
            age_limit=summary_data.get("age_limit"),
            application_deadline=summary_data.get("application_deadline"),
            pay_scale=summary_data.get("pay_scale"),
            employment_type=summary_data.get("employment_type"),
            overall_skill=summary_data.get("overall_skill"),
        )

        print(f"[✅ SAVED] {pdf_name}")
        return "downloaded"

    except requests.exceptions.SSLError as ssl_error:
        print(f"[SSL ERROR] {pdf_url}: {ssl_error}")
        return "error"
    except requests.exceptions.RequestException as e:
        print(f"[NETWORK ERROR] {pdf_url}: {e}")
        return "error"
    except Exception as e:
        print(f"[PROCESSING ERROR] {pdf_url}: {e}")
        return "error"

# Main processor
def process_all_pdfs(source_url):
    print(f"\n[DEBUG] Starting scrape from: {source_url}")
    pdf_links = get_pdf_links_from_url(source_url)
    print(f"[DEBUG] Found {len(pdf_links)} PDF links.")

    if not pdf_links:
        print("[DEBUG] No PDF links found. Exiting.")
        return []

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    results = []
    downloaded = 0
    skipped = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_pdf = {
            executor.submit(process_pdf, pdf_url, source_url, session): pdf_url
            for pdf_url in pdf_links
        }

        for future in as_completed(future_to_pdf):
            result = future.result()
            if result == "downloaded":
                downloaded += 1
            elif result == "skipped":
                skipped += 1
            else:
                errors += 1

    print(f"\n[SUMMARY] Total PDFs: {len(pdf_links)}, Downloaded: {downloaded}, Skipped: {skipped}, Errors: {errors}")
    return results

# Run across all websites
def run_scraper():
    websites = [
        "https://chandigarh.gov.in/information/public-notices",  # Add more here
    ]
    for site in websites:
        print(f"\nScraping site: {site}")
        process_all_pdfs(site)