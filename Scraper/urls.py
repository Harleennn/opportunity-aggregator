# Available Routes:
# http://localhost:8000/run-scraper/
# http://localhost:8000/summaries/


from django.urls import path
from . import views

urlpatterns = [
    path("", views.scrape_and_show, name="scrape_and_show"),
    path("run-scraper/", views.run_scraper_view, name="run_scraper"),  # 👈 ADD THIS
]

