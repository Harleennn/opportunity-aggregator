from django.shortcuts import render, redirect
from .utils import run_scraper
from .models import JobSummary

def scrape_and_show(request):
    if request.method == "POST":
        run_scraper()
        return redirect("scrape_and_show")  # Reload the page to show new results

    summaries = JobSummary.objects.all().order_by("-created_at")
    return render(request, "scraper/summary.html", {"summaries": summaries})
