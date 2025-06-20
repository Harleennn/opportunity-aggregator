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


def mock_llm_summarize(text):
    return text[:500] + "..."


#  Setup browser 
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Updated headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--remote-debugging-port=9222")
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
            links.append(full_href)

    driver.quit()
    return links


def process_all_pdfs(source_url):
    pdf_links = get_pdf_links_from_url(source_url)
    results = []

    for pdf_url in pdf_links:
        try:
            print(f" Downloading: {pdf_url}")
            response = requests.get(pdf_url, verify=False)
            pdf_bytes = BytesIO(response.content)
            pdf_name = pdf_url.split("/")[-1]

            text = extract_text_normal(pdf_bytes.getvalue())

            if len(text.strip()) < 50:
                text = extract_text_ocr(pdf_bytes.getvalue())

            summary = mock_llm_summarize(text)

            # Save to DB
            job_summary = JobSummary.objects.create(
                source_url=source_url,
                pdf_name=pdf_name,
                summary_text=summary,
            )

            results.append({
                "pdf_name": pdf_name,
                "summary": summary,
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
        "https://pesco.punjab.gov.in/Advertisement",  #  current site
      
    ]

    for site in websites:
        print(f"\n Scraping site: {site}")
        process_all_pdfs(site)
