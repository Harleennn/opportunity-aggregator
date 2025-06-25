from django.shortcuts import render
from .utils import process_all_pdfs
from .models import JobSummary
import threading

# Define list of websites (can add more later)
SCRAPE_SITES = [
    "https://chandigarh.gov.in/information/public-notices",
    # Add more URLs here
]

def background_scrape(sites):
    for site in sites:
        print(f"[ASYNC] Background scraping: {site}")
        process_all_pdfs(site)
        print(f"[ASYNC] Done scraping: {site}")

def scrape_and_show(request):
    #  Start scraping in background
    threading.Thread(target=background_scrape, args=(SCRAPE_SITES,)).start()

    #  Show existing data from DB (doesn't wait for new scrape to finish)
    summaries = JobSummary.objects.filter(source_url__in=SCRAPE_SITES).order_by('-created_at')[:50]
    
    return render(request, "scraper/summary.html", {"summaries": summaries})




# def scrape_and_show(request):
#     source_url = "https://chdsw.gov.in/index.php/recruitments/index"
#     process_all_pdfs(source_url)

#     # 👇 TEMPORARY — add a fake record
#     JobSummary.objects.create(
#         source_url=source_url,
#         pdf_name="Test.pdf",
#         title="Test Job",
#         eligibility="Any graduate",
#         minimum_qualification="None",
#         age_limit="18-35",
#         application_deadline="31 July 2025",
#         pay_scale="20,000 INR",
#         employment_type="Contract",
#         overall_skill="Typing, Communication"
#     )

#     summaries = JobSummary.objects.filter(source_url=source_url).order_by('-created_at')
#     return render(request, "scraper/summary.html", {"summaries": summaries})
