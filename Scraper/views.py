from django.shortcuts import render
from .scraper_utils.job_processor import process_all_pdfs
from .models import JobPosting
import threading
from .models import JobDetails  
from .scraper_utils.recommendor import recommend_jobs


SCRAPE_SITES = [
        # "https://www.nielit.gov.in/chandigarh/recruitments",
        # "http://nrhmchd.gov.in/pages/page/recruitments",
        # "https://gmch.gov.in/jobs-and-training",
        "https://chandigarh.gov.in/information/public-notices",
]

# Background thread that scrapes all sites
def background_scrape(sites):
    for site in sites:
        print(f"[ASYNC] Background scraping: {site}")
        process_all_pdfs(site)
        print(f"[ASYNC] Done scraping: {site}")

# Main view function
def scrape_and_show(request):
    # Start background scraping thread
    # threading.Thread(target=background_scrape, args=(SCRAPE_SITES,)).start()

    # Get all job postings (you CANNOT use select_related for reverse relation)
    postings = JobPosting.objects.filter(source__url__in=SCRAPE_SITES)\
        .order_by('-scraped_at')[:50]

    # Get latest scraped timestamp
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

    
