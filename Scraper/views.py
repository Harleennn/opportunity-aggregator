from django.shortcuts import render
from .utils import process_all_pdfs
from .models import JobSummary

def scrape_and_show(request):
    source_url = "https://chandigarh.gov.in/information/public-notices"  # using test site for now
    process_all_pdfs(source_url)  

  
    summaries = JobSummary.objects.filter(source_url=source_url).order_by('-created_at')

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
