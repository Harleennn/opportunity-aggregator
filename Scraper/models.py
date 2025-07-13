from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.name

class JobPosting(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    pdf_name = models.CharField(max_length=255)
    pdf_url = models.URLField()
    scraped_at = models.DateTimeField(auto_now_add=True)

    # These are PDF-wide values
    age_limit = models.CharField(max_length=100, blank=True, null=True)
    application_deadline = models.CharField(max_length=100, blank=True, null=True)
    pay_scale = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.pdf_name

class JobDetails(models.Model):
    posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="jobdetails")
    
    # These are job-specific
    title = models.CharField(max_length=255)
    eligibility = models.TextField(blank=True, null=True)
    minimum_qualification = models.TextField(blank=True, null=True)
    overall_skill = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)  # ✅ LLM Summary field

    def __str__(self):
        return self.title
