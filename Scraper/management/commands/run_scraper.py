from django.core.management.base import BaseCommand
from Scraper.scraper_utils.Run_scraper import run_scraper

class Command(BaseCommand):
    help = 'Runs the job scraper and stores summaries in the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write(" Starting the scraper...")
        run_scraper()
        self.stdout.write(self.style.SUCCESS(" Scraping completed successfully."))
