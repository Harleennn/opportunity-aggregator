# this file is extracting PDF links from webpages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time

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

    anchors = driver.find_elements(By.TAG_NAME, 'a')
    links = []
    for link in anchors:
        href = link.get_attribute("href")
        if href and href.endswith(".pdf"):
            full_href = urljoin(url, href)
            links.append(full_href)

    driver.quit()

    unique_links = list(set(links))  # Remove duplicates
    print(f"[INFO] Found {len(unique_links)} PDF(s) at {url}")
    return unique_links
