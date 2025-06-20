from django.shortcuts import render
from .utils import process_all_pdfs

def scrape_and_show(request):
    source_url = "https://pesco.punjab.gov.in/Advertisement"
    summaries = process_all_pdfs(source_url)
    return render (request, "scraper/summary.html",{"summaries": summaries})