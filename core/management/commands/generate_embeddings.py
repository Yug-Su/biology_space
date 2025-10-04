"""
Management command to generate embeddings for articles
Usage: python manage.py generate_embeddings
"""

from django.core.management.base import BaseCommand
from core.services.embeddings import embedding_service
import asyncio


class Command(BaseCommand):
    help = 'Generate embeddings for all articles'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting embedding generation...'))

        asyncio.run(self._async_handle())

    async def _async_handle(self):
        try:
            async for progress in embedding_service.embed_all_articles():
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{progress['progress']}/{progress['total']}] {progress['article']}"
                    )
                )

            self.stdout.write(
                self.style.SUCCESS('All embeddings generated successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating embeddings: {e}')
            )
