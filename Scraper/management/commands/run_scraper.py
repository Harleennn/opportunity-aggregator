from django.core.management.base import BaseCommand
from Scraper.utils import run_scraper  # update this import if your file is named differently

class Command(BaseCommand):
    help = 'Runs the job scraper and stores summaries in the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting the scraper...")
        run_scraper()
        self.stdout.write(self.style.SUCCESS("✅ Scraping completed successfully."))
