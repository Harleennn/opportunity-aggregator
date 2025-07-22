from django.shortcuts import render
from .scraper_utils.job_processor import process_all_pdfs
from .models import JobPosting, JobDetails
import threading
from .scraper_utils.recommendor import recommend_jobs
from django.http import JsonResponse
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

SCRAPE_SITES = [
    # "https://www.nielit.gov.in/chandigarh/recruitments",
    # "http://nrhmchd.gov.in/pages/page/recruitments",
    # "https://gmch.gov.in/jobs-and-training",
    "https://chandigarh.gov.in/information/public-notices",
]

# Optional: run this in background for auto-scraping if needed
def background_scrape(sites):
    for site in sites:
        print(f"[ASYNC] Background scraping: {site}")
        process_all_pdfs(site)
        print(f"[ASYNC] Done scraping: {site}")



@csrf_exempt
def summary_json(request):
    output = []

    postings = JobPosting.objects.prefetch_related('jobdetails', 'source').all()

    for post in postings:
        try:
            details = JobDetails.objects.filter(posting=post).first()
            if details and details.summary and details.title:
                job_data = {
                    "title": details.title,            #  Use the LLM-generated title
                    "summary": details.summary,        #  Use the summary from LLM
                    "url": post.pdf_url                #  Link to the job PDF
                }
                output.append(job_data)
        except Exception as e:
            print(f"Error in summary_json: {e}")
            continue

    return JsonResponse(output, safe=False)
#  Renders the HTML page using frontend/jobs.html template
def jobs_page(request):
    return render(request, "jobs.html")  # Make sure this file is in the frontend/ folder




# View for Django admin or summary.html page (optional)
# def scrape_and_show(request):
#     postings = JobPosting.objects.filter(source__url__in=SCRAPE_SITES)\
#         .prefetch_related('jobdetails')\
#         .order_by('-scraped_at')[:50]

#     last_scraped = postings[0].scraped_at if postings else None

#     return render(
#         request,
#         "scraper/summary.html",
#         {"postings": postings, "last_scraped": last_scraped}
#     )

# # Recommendation view (optional UI)
# def recommend_view(request):
#     recommended_jobs = []
#     query = ""

#     if request.method == "POST":
#         query = request.POST.get("skills", "")
#         if query:
#             jobs = JobDetails.objects.select_related("posting", "posting__source").all()
#             recommended_jobs = recommend_jobs(query, jobs)

#     return render(request, "scraper/recommend.html", {
#         "recommended_jobs": recommended_jobs,
#         "query": query
#     })