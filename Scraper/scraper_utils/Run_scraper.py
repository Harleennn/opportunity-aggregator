import threading
from .job_processor import process_all_pdfs

def run_scraper():
    websites = [
        "https://chandigarh.gov.in/information/public-notices",
        "https://chdsw.gov.in/index.php/recruitments/index",
    ]

    threads = []

    for site in websites:
        print(f"\n[STARTING] Scraping site: {site}")
        t = threading.Thread(target=process_all_pdfs, args=(site,))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print("\n All sites scraped.")
