
from django.db import models

class JobSummary(models.Model):
    source_url = models.URLField()
    pdf_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    minimum_qualification = models.TextField(blank=True, null=True)
    age_limit = models.CharField(max_length=100, blank=True, null=True)
    application_deadline = models.CharField(max_length=100, blank=True, null=True)
    pay_scale = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=100, blank=True, null=True)
    overall_skill = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pdf_name
