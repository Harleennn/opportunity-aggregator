from django.contrib import admin
from django.urls import path, include  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scraper/', include('Scraper.urls')),  #  This connects scraper views
]
