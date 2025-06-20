from django.db import models

class JobSummary(models.Model):
    source_url = models.URLField()
    pdf_name = models.CharField(max_length=255)
    summary_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pdf_name
