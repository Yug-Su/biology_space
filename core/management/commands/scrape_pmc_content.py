"""
Management command to scrape full content from PubMed Central using Scrapy
Usage: python manage.py scrape_pmc_content --limit 200
"""

from django.core.management.base import BaseCommand
from core.models import Article
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import time
import threading


class PMCSpider(scrapy.Spider):
    """Scrapy spider to scrape PMC articles"""
    name = 'pmc_spider'

    custom_settings = {
        'CONCURRENT_REQUESTS': 3,  # Limit concurrent requests
        'DOWNLOAD_DELAY': 0.5,  # 500ms between requests (2 req/sec)
        'ROBOTSTXT_OBEY': False,  # Educational hackathon use only
        'USER_AGENT': 'SpaceBio Research Platform (Educational/Research)',
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, articles, command, *args, **kwargs):
        super(PMCSpider, self).__init__(*args, **kwargs)
        self.articles = articles
        self.command = command
        self.success_count = 0
        self.error_count = 0
        self.total = len(articles)
        self.scraped_data = []  # Buffer to store data for later saving

    def start_requests(self):
        """Generate requests for each article"""
        for article in self.articles:
            # Extract PMC ID (remove PMC prefix if present)
            pmc_id = article.pmc_id.replace('PMC', '')
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/"

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'article': article, 'pmc_id': pmc_id},
                errback=self.handle_error
            )

    def parse(self, response):
        """Parse PMC article page"""
        article = response.meta['article']
        pmc_id = response.meta['pmc_id']

        try:
            sections = []

            # 1. Abstract
            abstract = response.css('div.abstract ::text').getall()
            if abstract:
                abstract_text = ' '.join(abstract).strip()
                sections.append(f"ABSTRACT:\n{abstract_text[:2000]}")

            # 2. Introduction
            intro = response.xpath('//*[contains(translate(@id, "INTRO", "intro"), "intro")]//text()').getall()
            if not intro:
                intro = response.xpath('//h2[contains(translate(text(), "INTRODUCTION", "introduction"), "introduction")]/following-sibling::*[1]//text()').getall()

            if intro:
                intro_text = ' '.join(intro).strip()
                sections.append(f"INTRODUCTION:\n{intro_text[:1200]}")

            # 3. Results/Discussion
            results = response.xpath('//*[contains(translate(@id, "RESULT", "result"), "result") or contains(translate(@id, "DISCUSSION", "discussion"), "discussion")]//text()').getall()
            if not results:
                results = response.xpath('//h2[contains(translate(text(), "RESULTS", "results"), "results") or contains(translate(text(), "DISCUSSION", "discussion"), "discussion")]/following-sibling::*[1]//text()').getall()

            if results:
                results_text = ' '.join(results).strip()
                sections.append(f"RESULTS:\n{results_text[:1200]}")

            # 4. Methods (important for scientific articles)
            methods = response.xpath('//*[contains(translate(@id, "METHOD", "method"), "method")]//text()').getall()
            if not methods:
                methods = response.xpath('//h2[contains(translate(text(), "METHODS", "methods"), "methods")]/following-sibling::*[1]//text()').getall()

            if methods:
                methods_text = ' '.join(methods).strip()
                sections.append(f"METHODS:\n{methods_text[:800]}")

            # 5. Conclusion
            conclusion = response.xpath('//*[contains(translate(@id, "CONCLUSION", "conclusion"), "conclusion")]//text()').getall()
            if not conclusion:
                conclusion = response.xpath('//h2[contains(translate(text(), "CONCLUSION", "conclusion"), "conclusion")]/following-sibling::*[1]//text()').getall()

            if conclusion:
                conclusion_text = ' '.join(conclusion).strip()
                sections.append(f"CONCLUSION:\n{conclusion_text[:1000]}")

            # Combine all sections
            full_content = "\n\n".join(sections)

            if full_content:
                # Buffer data for later saving (avoid Django async issues)
                self.scraped_data.append({
                    'article': article,
                    'content': full_content,
                    'pmc_id': pmc_id
                })

                self.success_count += 1
                self.command.stdout.write(
                    self.command.style.SUCCESS(
                        f"[{self.success_count + self.error_count}/{self.total}] OK PMC{pmc_id}: {len(full_content)} chars"
                    )
                )
            else:
                raise Exception("No content extracted")

        except Exception as e:
            self.error_count += 1
            self.command.stdout.write(
                self.command.style.ERROR(
                    f"[{self.success_count + self.error_count}/{self.total}] ERROR PMC{pmc_id}: {str(e)[:80]}"
                )
            )

    def handle_error(self, failure):
        """Handle request errors"""
        self.error_count += 1
        request = failure.request
        pmc_id = request.meta.get('pmc_id', 'unknown')
        try:
            error_msg = str(failure.value)[:100]
        except:
            error_msg = "Unknown error"
        self.command.stdout.write(
            self.command.style.ERROR(
                f"ERROR Request failed for PMC{pmc_id}: {error_msg}"
            )
        )

    def closed(self, reason):
        """Called when spider finishes - save all scraped data"""
        # Save in a separate thread to avoid async context issues
        def save_data():
            from django import db
            db.connections.close_all()  # Close any async connections

            saved_count = 0
            for data in self.scraped_data:
                try:
                    data['article'].content = data['content']
                    data['article'].save(update_fields=['content'])
                    saved_count += 1
                except Exception as e:
                    self.command.stdout.write(
                        self.command.style.ERROR(f"Failed to save PMC{data['pmc_id']}: {str(e)[:80]}")
                    )

            self.command.stdout.write(
                self.command.style.SUCCESS(
                    f"\nScraping complete! Scraped: {self.success_count}, Saved: {saved_count}, Errors: {self.error_count}"
                )
            )

        # Run save in thread
        thread = threading.Thread(target=save_data)
        thread.start()
        thread.join()  # Wait for save to complete


class Command(BaseCommand):
    help = 'Scrape full content from PMC for articles using Scrapy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=200,
            help='Number of articles to scrape (default: 200)'
        )

    def handle(self, *args, **options):
        limit = options['limit']

        # Get articles with PMC IDs
        articles = list(Article.objects.filter(
            pmc_id__isnull=False
        ).exclude(
            pmc_id=''
        )[:limit])

        total = len(articles)

        if total == 0:
            self.stdout.write(self.style.WARNING('No articles with PMC IDs found'))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting PMC scraping for {total} articles with Scrapy...\n'
            )
        )

        # Configure and run Scrapy spider
        process = CrawlerProcess({
            'USER_AGENT': 'SpaceBio Research Platform (Educational/Research)',
            'ROBOTSTXT_OBEY': False,  # Educational hackathon use only
            'CONCURRENT_REQUESTS': 3,
            'DOWNLOAD_DELAY': 0.5,
            'LOG_LEVEL': 'WARNING',  # Reduce Scrapy logs
        })

        process.crawl(PMCSpider, articles=articles, command=self)
        process.start()
