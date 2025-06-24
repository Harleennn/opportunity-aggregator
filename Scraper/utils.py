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
from urllib.parse import urljoin  
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context

KEYWORDS_IN_URL = ['recruitment', 'vacancy', 'job', 'employment', 'engagement']
TEXT_KEYWORDS = ['recruitment', 'vacancy', 'invites application', 'job', 'posts available', 'engagement']
REQUIRED_YEAR = '2025'



def mock_llm_summarize(text):
    # This should be replaced with real LLM logic
    return {
        "title": "Consultant (Retired Doctor)",
        "eligibility": "Retired from Govt. Medical Service",
        "minimum_qualification": "MBBS with Post-Graduation",
        "age_limit": "Below 65 years",
        "application_deadline": "15 July 2025",
        "pay_scale": "Rs. 75,000 per month",
        "employment_type": "Contractual",
        "overall_skill": "Medical expertise, patient handling"
    }

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
            href_lower = full_href.lower()

            if any(k in href_lower for k in KEYWORDS_IN_URL) and REQUIRED_YEAR in href_lower:
                links.append(full_href)

    driver.quit()
    return links



def process_all_pdfs(source_url):
    pdf_links = get_pdf_links_from_url(source_url)
    results = []

    for pdf_url in pdf_links:
        try:
            print(f"\n Downloading: {pdf_url}")
            response = requests.get(pdf_url, verify=False)
            pdf_bytes = BytesIO(response.content)
            pdf_name = pdf_url.split("/")[-1]

            text = extract_text_normal(pdf_bytes.getvalue())
            if len(text.strip()) < 50:
                text = extract_text_ocr(pdf_bytes.getvalue())

            if not any(kw in text.lower() for kw in TEXT_KEYWORDS):
                print(f" Skipped (not job related): {pdf_name}")
                continue

            # Use actual LLM here
            summary_data = mock_llm_summarize(text)

            # Save each field to model
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

        except Exception as e:
            print(f" Error with {pdf_url}: {e}")
            continue

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
        "https://gmch.gov.in/jobs-and-training",  # Test Site
    ]
    for site in websites:
        print(f"\n Scraping site: {site}")
        process_all_pdfs(site)
