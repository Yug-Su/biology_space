"""
Django models for SpaceBio Platform
SQLite compatible version
"""

from django.db import models
import uuid
import json


class Article(models.Model):
    """
    Scientific article from PMC database

    Fields:
    - title: Article title
    - abstract: Article abstract/summary
    - pmc_id: PubMed Central ID (unique)
    - url: Link to PMC article
    - authors: List of authors
    - keywords: Extracted keywords
    - content: Full article content (scraped)
    - publication_date: Date of publication
    - created_at: When added to our database
    """

    title = models.TextField()
    abstract = models.TextField(blank=True, null=True)
    pmc_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    url = models.URLField(max_length=500)

    # JSON fields for authors and keywords (SQLite compatible)
    authors = models.JSONField(default=list, blank=True)
    keywords = models.JSONField(default=list, blank=True)

    # Full content
    content = models.TextField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Search optimization
    views_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-publication_date', '-created_at']
        indexes = [
            models.Index(fields=['pmc_id']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title[:100]}..."

    def increment_views(self):
        """Increment view counter"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ArticleEmbedding(models.Model):
    """
    Vector embeddings for semantic search
    SQLite version: stores embeddings as JSON array
    """

    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name='embedding'
    )

    # Embedding stored as JSON array (dimension 1536 for OpenAI)
    embedding = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['article']),
        ]

    def __str__(self):
        return f"Embedding for: {self.article.title[:50]}"

    @staticmethod
    def cosine_similarity(vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        import math
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        return dot_product / (magnitude1 * magnitude2)


class ChatSession(models.Model):
    """
    User chat session with AI assistant

    Stores conversation history for context
    """

    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user_identifier = models.CharField(max_length=100, blank=True, null=True)  # Optional user tracking

    # JSON field for message history
    messages = models.JSONField(default=list)

    # Session metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user_identifier']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Session {self.session_id} - {len(self.messages)} messages"

    def add_message(self, role: str, content: str):
        """Add message to conversation"""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': str(models.functions.Now())
        })
        self.save()

    def get_recent_messages(self, limit: int = 10):
        """Get recent conversation messages"""
        return self.messages[-limit:]


class SearchQuery(models.Model):
    """
    Track search queries for analytics

    Helps understand user behavior and improve search
    """

    query_text = models.TextField()
    results_count = models.IntegerField(default=0)
    user_identifier = models.CharField(max_length=100, blank=True, null=True)

    # Top result clicked (if any)
    clicked_article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_clicks'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query_text']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.query_text[:50]} ({self.results_count} results)"


class GeneratedArticle(models.Model):
    """
    AI-generated articles
    """

    title = models.TextField()
    content = models.TextField()

    # Generation parameters
    topic = models.CharField(max_length=500)
    article_type = models.CharField(max_length=50)  # review, research, protocol
    length = models.CharField(max_length=20)  # short, medium, long
    style = models.CharField(max_length=50)  # academic, executive, technical

    # Source articles used for generation
    source_articles = models.ManyToManyField(Article, blank=True, related_name='generated_from')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    generation_time_seconds = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Generated: {self.title[:100]}"
