import requests
from bs4 import BeautifulSoup  
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes
from io import BytesIO
from .models import JobSummary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from urllib.parse import urljoin, urlparse
import certifi
import warnings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

KEYWORDS_IN_URL = ['recruitment', 'vacancy', 'job', 'employment', 'engagement']
TEXT_KEYWORDS = ['recruitment', 'vacancy', 'invites application', 'job', 'posts available', 'engagement']
REQUIRED_YEAR = ['2023', '2024', '2025']


def mock_llm_summarize(text, pdf_name=None):
    # This should be replaced with real LLM logic
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


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)


def get_pdf_links_from_url(url):
    driver = get_driver()
    driver.get(url)
    time.sleep(5)

    links = []
    anchors = driver.find_elements(By.TAG_NAME, 'a')
    
    for link in anchors:
        href = link.get_attribute("href")
        if href and href.endswith(".pdf"):
            full_href = urljoin(url, href)
            print(f"[DEBUG] Found PDF link: {full_href}")
            links.append(full_href)
    driver.quit()
    return links


def process_all_pdfs(source_url):
    print(f"\n[DEBUG] Starting scrape from: {source_url}")
    pdf_links = get_pdf_links_from_url(source_url)
    print(f"[DEBUG] Found {len(pdf_links)} PDF links.")
    if not pdf_links:
        print("[DEBUG] No PDF links found. Exiting.")
        return []

    results = []
    skipped = 0
    downloaded = 0
    errors = 0

    # Setup session with retries
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    for pdf_url in pdf_links:
        try:
            # Convert http to https if needed
            if pdf_url.startswith("http://"):
                pdf_url = pdf_url.replace("http://", "https://")

            print(f"\n Downloading: {pdf_url}")
            response = session.get(pdf_url, timeout=10, verify=certifi.where())
            response.raise_for_status()

            pdf_bytes = BytesIO(response.content)
            pdf_name = pdf_url.split("/")[-1]

            text = extract_text_normal(pdf_bytes.getvalue())
            if len(text.strip()) < 50:
                text = extract_text_ocr(pdf_bytes.getvalue())

            if not any(kw in text.lower() for kw in TEXT_KEYWORDS):
                print(f" Skipped (not job related): {pdf_name}")
                skipped += 1
                continue

            
            summary_data = mock_llm_summarize(text, pdf_name=pdf_name)

            # Save to DB
            job_summary = JobSummary.objects.create(
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

            results.append({
                "pdf_name": pdf_name,
                **summary_data
            })
            downloaded += 1

        except requests.exceptions.RequestException as e:
            print(f"[NETWORK ERROR] {pdf_url}: {e}")
            errors += 1
            continue
        except Exception as e:
            print(f"[PROCESSING ERROR] {pdf_url}: {e}")
            errors += 1
            continue

    print(f"\n[SUMMARY] Total PDFs: {len(pdf_links)}, Downloaded: {downloaded}, Skipped: {skipped}, Errors: {errors}")
    return results


def extract_text_normal(pdf_bytes):
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_text_ocr(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text


def run_scraper():
    websites = [
        "https://chandigarh.gov.in/information/public-notices",  # Test Site
    ]
    for site in websites:
        print(f"\n Scraping site: {site}")
        process_all_pdfs(site)
