from django.contrib import admin
from django.urls import path, include
from Scraper.views import summary_json  # ✅ Import directly

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scraper/', include('Scraper.urls')),
    path('api/summaries/', summary_json, name='summary_json'),  # ✅ Expose it at root level
]
