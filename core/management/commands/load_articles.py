"""
Management command to load articles from CSV
Usage: python manage.py load_articles
"""

from django.core.management.base import BaseCommand
from core.models import Article
import csv
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Load articles from CSV file into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='Data/SB_publication_PMC.csv',
            help='Path to CSV file'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        base_dir = settings.BASE_DIR
        file_path = os.path.join(base_dir, csv_file)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Loading articles from: {file_path}'))

        # Clear existing articles
        Article.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing articles'))

        loaded_count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            # Remove BOM if present
            first_char = f.read(1)
            if first_char != '\ufeff':
                f.seek(0)

            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Extract PMC ID from URL
                    pmc_id = None
                    url = row.get('Link', '').strip()
                    if 'PMC' in url:
                        pmc_id = url.split('/')[-2]  # Extract PMC ID from URL

                    article = Article.objects.create(
                        title=row.get('Title', '').strip(),
                        url=url,
                        pmc_id=pmc_id,
                        # We don't have abstract/authors in CSV, will be scraped later
                        abstract=None,
                        authors=[],
                        keywords=[],
                        content=None,
                        publication_date=None
                    )
                    loaded_count += 1

                    if loaded_count % 50 == 0:
                        self.stdout.write(
                            self.style.SUCCESS(f'Loaded {loaded_count} articles...')
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error loading article: {row.get("Title", "Unknown")}: {e}')
                    )
                    continue

        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {loaded_count} articles!')
        )
