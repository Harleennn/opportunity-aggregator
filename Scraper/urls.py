# http://localhost:8000/scraper/summary/
#http://localhost:8000/admin/

from django.urls import path, include
from . import views  

urlpatterns = [
   path("summary/", views.scrape_and_show, name="scrape_and_show"),
   path("recommend/", views.recommend_view, name="recommend_jobs"),
]
