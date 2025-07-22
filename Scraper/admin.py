# admin.py
from django.contrib import admin
from .models import Source, JobPosting, JobDetails

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')  # Show columns in admin list view
                  

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf_name', 'pdf_url', 'source', 'scraped_at')
    

@admin.register(JobDetails)
class JobDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'posting', 'summary')  # posting shows which PDF this job belongs to
   
