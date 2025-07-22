# http://localhost:8000/scraper/summary/
#http://localhost:8000/admin/
# http://localhost:8000/scraper/recommend/
# http://localhost:8000/scraper/api/summaries/
# http://localhost:8000/api/summaries/
from django.urls import path
from . import views
from .views import summary_json

urlpatterns = [
    path('api/summaries/', summary_json, name='summary-json'),
    path("jobs/", views.jobs_page, name="jobs_page"),  # for frontend/jobs.html
]


