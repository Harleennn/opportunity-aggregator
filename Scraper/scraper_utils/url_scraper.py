# scraper_utils/url_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin, urlparse
import time
import requests
from bs4 import BeautifulSoup

# 1. Entry point: try static first, fallback to Selenium
def get_pdf_links_from_url(url):
    try:
        print(f"[INFO] Trying static scraper for {url}")
        pdfs = simple_scraper(url)
        if pdfs:
            return pdfs
        else:
            print(f"[INFO] Static scraper returned no PDFs. Trying Selenium for {url}")
            return selenium_scraper(url)
    except Exception as e:
        print(f"[ERROR] Static scraper failed. Trying Selenium: {e}")
        return selenium_scraper(url)

# 2. Static scraper (uses BeautifulSoup)
def simple_scraper(start_url):
    pdf_links = []
    base_url = f"{urlparse(start_url).scheme}://{urlparse(start_url).netloc}"

    try:
        response = requests.get(start_url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("table.table-bordered tbody tr")

        for row in rows:
            detail_anchor = row.find("a")
            if not detail_anchor:
                continue

            detail_url = urljoin(base_url, detail_anchor.get("href"))
            detail_response = requests.get(detail_url, timeout=10)
            detail_soup = BeautifulSoup(detail_response.content, "html.parser")

            pdf_anchor = detail_soup.find("a", href=lambda x: x and x.endswith(".pdf"))
            if pdf_anchor:
                pdf_url = urljoin(base_url, pdf_anchor.get("href"))
                print(f"[FOUND - STATIC] {pdf_url}")
                pdf_links.append(pdf_url)
    except Exception as e:
        print(f"[ERROR] Static scrape failed for {start_url}: {e}")

    return list(set(pdf_links))

# 3. JS-heavy scraper (uses Selenium)
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)

def selenium_scraper(url):
    links = []
    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(5)

        anchors = driver.find_elements(By.TAG_NAME, 'a')
        for link in anchors:
            href = link.get_attribute("href")
            if href and href.endswith(".pdf"):
                full_href = urljoin(url, href)
                # print(f"[FOUND - SELENIUM] {full_href}")
                links.append(full_href)

    except Exception as e:
        print(f"[ERROR] Selenium scrape failed for {url}: {e}")
    finally:
        driver.quit()

    unique_links = list(set(links))
    print(f"[INFO] Found {len(unique_links)} PDF(s) at {url}")
    return unique_links
