

# Register your models here.
from django.contrib import admin
from .models import Source, JobPosting, JobDetails

admin.site.register(Source)
admin.site.register(JobPosting)
admin.site.register(JobDetails)
