"""
Embeddings Service - Generate and search semantic vectors
Uses sentence-transformers (all-MiniLM-L6-v2) for FREE local embeddings
"""

from sentence_transformers import SentenceTransformer
from django.conf import settings
from core.models import Article, ArticleEmbedding
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service to generate and manage embeddings for semantic search
    Uses sentence-transformers locally (100% free, no API needed)
    """

    def __init__(self):
        # Use local sentence-transformers model (all-MiniLM-L6-v2)
        # This model produces 384-dimensional embeddings
        self.model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self._model = None

    @property
    def model(self):
        """Lazy load the model on first use"""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully")
        return self._model

    async def generate_embedding(self, text: str) -> list:
        """
        Generate embedding vector for text using local model

        Args:
            text: Text to embed

        Returns:
            List of floats (embedding vector, 384 dimensions)
        """
        @sync_to_async
        def encode_text():
            # Limit text length to avoid memory issues
            text_truncated = text[:5000]
            embedding = self.model.encode(text_truncated, convert_to_tensor=False)
            return embedding.tolist()

        try:
            return await encode_text()
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise Exception(f"Failed to generate embedding: {str(e)}")

    async def embed_article(self, article: Article) -> ArticleEmbedding:
        """
        Generate and save embedding for an article

        Args:
            article: Article instance

        Returns:
            ArticleEmbedding instance
        """
        # Use full PMC content if available, otherwise use abstract
        content_text = article.content if article.content else (article.abstract or '')
        text_to_embed = f"{article.title}\n\n{content_text}"

        embedding_vector = await self.generate_embedding(text_to_embed)

        # Save or update embedding (use sync_to_async for ORM)
        @sync_to_async
        def save_embedding():
            return ArticleEmbedding.objects.update_or_create(
                article=article,
                defaults={'embedding': embedding_vector}
            )

        embedding, created = await save_embedding()

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
        @sync_to_async
        def get_articles_without_embeddings():
            return list(Article.objects.filter(embedding__isnull=True))

        @sync_to_async
        def count_articles():
            return Article.objects.filter(embedding__isnull=True).count()

        articles_without_embeddings = await get_articles_without_embeddings()
        total = len(articles_without_embeddings)
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

        # Get all embeddings (use sync_to_async for ORM)
        @sync_to_async
        def get_embeddings():
            return list(ArticleEmbedding.objects.select_related('article').all())

        embeddings = await get_embeddings()

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
