from django.shortcuts import render
from .utils import process_all_pdfs
from .models import JobSummary

def scrape_and_show(request):
    source_url = "https://gmch.gov.in/jobs-and-training"  # using test site for now
    process_all_pdfs(source_url)  

  
    summaries = JobSummary.objects.filter(source_url=source_url).order_by('-created_at')

    return render(request, "scraper/summary.html", {"summaries": summaries})
