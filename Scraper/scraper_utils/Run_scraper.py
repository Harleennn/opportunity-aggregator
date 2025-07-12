import threading
from .job_processor import process_all_pdfs

def run_scraper():
    websites = [
        # "https://www.nielit.gov.in/chandigarh/recruitments",
        # "http://nrhmchd.gov.in/pages/page/recruitments",
        # "https://gmch.gov.in/jobs-and-training",
        "https://chandigarh.gov.in/information/public-notices",
    
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
