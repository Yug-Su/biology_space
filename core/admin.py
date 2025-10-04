from django.contrib import admin
from .models import Article, ArticleEmbedding, ChatSession, SearchQuery, GeneratedArticle


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title_short', 'pmc_id', 'publication_date', 'views_count', 'created_at']
    list_filter = ['publication_date', 'created_at']
    search_fields = ['title', 'pmc_id', 'authors']
    readonly_fields = ['created_at', 'updated_at', 'views_count']

    def title_short(self, obj):
        return obj.title[:100] + '...' if len(obj.title) > 100 else obj.title
    title_short.short_description = 'Title'


@admin.register(ArticleEmbedding)
class ArticleEmbeddingAdmin(admin.ModelAdmin):
    list_display = ['article', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['article__title']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_identifier', 'message_count', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    search_fields = ['session_id', 'user_identifier']

    def message_count(self, obj):
        return len(obj.messages)
    message_count.short_description = 'Messages'


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query_short', 'results_count', 'clicked_article', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query_text']
    readonly_fields = ['created_at']

    def query_short(self, obj):
        return obj.query_text[:50] + '...' if len(obj.query_text) > 50 else obj.query_text
    query_short.short_description = 'Query'


@admin.register(GeneratedArticle)
class GeneratedArticleAdmin(admin.ModelAdmin):
    list_display = ['title_short', 'topic', 'article_type', 'length', 'style', 'created_at']
    list_filter = ['article_type', 'length', 'style', 'created_at']
    search_fields = ['title', 'topic']
    readonly_fields = ['created_at', 'generation_time_seconds']
    filter_horizontal = ['source_articles']

    def title_short(self, obj):
        return obj.title[:80] + '...' if len(obj.title) > 80 else obj.title
    title_short.short_description = 'Title'
