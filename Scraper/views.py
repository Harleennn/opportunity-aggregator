from django.shortcuts import render
from .scraper_utils.job_processor import process_all_pdfs
from .models import JobPosting, JobDetails
import threading
from .scraper_utils.recommendor import recommend_jobs

SCRAPE_SITES = [
    "https://chandigarh.gov.in/information/public-notices",
]

def background_scrape(sites):
    for site in sites:
        print(f"[ASYNC] Background scraping: {site}")
        process_all_pdfs(site)
        print(f"[ASYNC] Done scraping: {site}")

def scrape_and_show(request):
    # Fetch postings and prefetch the reverse FK 'jobdetails'
    postings = JobPosting.objects.filter(source__url__in=SCRAPE_SITES)\
        .prefetch_related('jobdetails')\
        .order_by('-scraped_at')[:50]

    last_scraped = postings[0].scraped_at if postings else None

    return render(
        request,
        "scraper/summary.html",
        {"postings": postings, "last_scraped": last_scraped}
    )

def recommend_view(request):
    recommended_jobs = []
    query = ""

    if request.method == "POST":
        query = request.POST.get("skills", "")
        if query:
            jobs = JobDetails.objects.select_related("posting", "posting__source").all()
            recommended_jobs = recommend_jobs(query, jobs)

    return render(request, "scraper/recommend.html", {
        "recommended_jobs": recommended_jobs,
        "query": query
    })
