from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.name

class JobPosting(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    pdf_name = models.CharField(max_length=255)
    pdf_url = models.URLField(unique=True)  # Make sure duplicates don't enter
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pdf_name

class JobDetails(models.Model):
    posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="jobdetails")
    title = models.CharField(max_length=255)
    summary = models.TextField()

    def __str__(self):
        return self.title
