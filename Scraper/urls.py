# http://localhost:8000/scraper/scrape/

from django.urls import path, include
from . import views  

urlpatterns = [
   path("summary/", views.scrape_and_show, name="scrape_and_show"),
]
