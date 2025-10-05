"""
Embeddings Service - Generate and search semantic vectors
Uses OpenAI text-embedding-3-small via OpenRouter
"""

import httpx
from django.conf import settings
from core.models import Article, ArticleEmbedding
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service to generate and manage embeddings for semantic search
    """

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.EMBEDDING_MODEL

    async def generate_embedding(self, text: str) -> list:
        """
        Generate embedding vector for text

        Args:
            text: Text to embed

        Returns:
            List of floats (embedding vector)
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "SpaceBio Platform"
                    },
                    json={
                        "model": self.model,
                        "input": text[:8000]  # Limit to 8000 chars
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data['data'][0]['embedding']

            except httpx.HTTPError as e:
                logger.error(f"Embedding API error: {e}")
                raise Exception(f"Failed to generate embedding: {str(e)}")

    async def embed_article(self, article: Article) -> ArticleEmbedding:
        """
        Generate and save embedding for an article

        Args:
            article: Article instance

        Returns:
            ArticleEmbedding instance
        """
        # Combine title (important) with content/abstract
        text_to_embed = f"{article.title}\n\n{article.abstract or ''}"

        embedding_vector = await self.generate_embedding(text_to_embed)

        # Save or update embedding
        embedding, created = ArticleEmbedding.objects.update_or_create(
            article=article,
            defaults={'embedding': embedding_vector}
        )

        action = "Created" if created else "Updated"
        logger.info(f"{action} embedding for article: {article.title[:50]}")

        return embedding

    async def embed_all_articles(self, batch_size: int = 10):
        """
        Generate embeddings for all articles without embeddings

        Args:
            batch_size: Number of articles to process in parallel

        Yields:
            Progress updates
        """
        articles_without_embeddings = Article.objects.filter(
            embedding__isnull=True
        )

        total = articles_without_embeddings.count()
        logger.info(f"Found {total} articles without embeddings")

        for i, article in enumerate(articles_without_embeddings):
            try:
                await self.embed_article(article)
                yield {
                    'progress': i + 1,
                    'total': total,
                    'article': article.title[:50]
                }

            except Exception as e:
                logger.error(f"Failed to embed article {article.id}: {e}")
                continue

    async def search_similar(self, query: str, limit: int = 20) -> list:
        """
        Search articles by semantic similarity

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of (article, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)

        # Get all embeddings
        embeddings = ArticleEmbedding.objects.select_related('article').all()

        # Calculate similarities
        results = []
        for emb in embeddings:
            similarity = ArticleEmbedding.cosine_similarity(
                query_embedding,
                emb.embedding
            )
            results.append((emb.article, similarity))

        # Sort by similarity (highest first)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]


# Singleton instance
embedding_service = EmbeddingService()
