from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Article, ChatSession, SearchQuery, GeneratedArticle, ArticleEmbedding
from .services.ai_providers import ai_provider
from .services.embeddings import embedding_service
import json
import asyncio
import uuid
import time


def home(request):
    """Homepage with search interface"""
    recent_articles = Article.objects.all()[:10]
    stats = {
        'total_articles': Article.objects.count(),
        'total_embeddings': ArticleEmbedding.objects.count(),
        'total_chats': ChatSession.objects.count(),
    }
    return render(request, 'core/home.html', {
        'recent_articles': recent_articles,
        'stats': stats
    })


def search(request):
    """Search articles - fallback to simple text search if no query"""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'simple')  # 'simple' or 'semantic'

    results = []

    if query:
        if search_type == 'semantic' and ArticleEmbedding.objects.exists():
            # Semantic search using embeddings
            try:
                results = asyncio.run(embedding_service.search_similar(query, limit=20))
                # Track search
                SearchQuery.objects.create(
                    query_text=query,
                    results_count=len(results)
                )
            except Exception as e:
                # Fallback to simple search on error
                results = Article.objects.filter(
                    Q(title__icontains=query) |
                    Q(abstract__icontains=query)
                )[:20]
        else:
            # Simple text search
            results = Article.objects.filter(
                Q(title__icontains=query) |
                Q(abstract__icontains=query)
            )[:20]

            # Track search
            SearchQuery.objects.create(
                query_text=query,
                results_count=len(results)
            )

    return render(request, 'core/search.html', {
        'query': query,
        'results': results,
        'search_type': search_type
    })


def article_detail(request, article_id):
    """Article detail page with AI summary option"""
    article = get_object_or_404(Article, id=article_id)
    article.increment_views()

    # Get similar articles if embeddings exist
    similar_articles = []
    if hasattr(article, 'embedding'):
        try:
            similar_results = asyncio.run(
                embedding_service.search_similar(article.title, limit=6)
            )
            similar_articles = [art for art, score in similar_results if art.id != article.id][:5]
        except:
            pass

    return render(request, 'core/article_detail.html', {
        'article': article,
        'similar_articles': similar_articles
    })


@csrf_exempt
@require_http_methods(["POST"])
def summarize_article(request, article_id):
    """Generate AI summary for article"""
    article = get_object_or_404(Article, id=article_id)

    try:
        data = json.loads(request.body)
        summary_type = data.get('type', 'concise')

        # Use abstract or title for summarization
        text_to_summarize = article.abstract or article.title

        summary = asyncio.run(
            ai_provider.summarize(text_to_summarize, summary_type=summary_type)
        )

        return JsonResponse({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def chat(request):
    """Chat interface with AI assistant"""
    session_id = request.session.get('chat_session_id')

    if session_id:
        try:
            chat_session = ChatSession.objects.get(session_id=session_id, is_active=True)
        except ChatSession.DoesNotExist:
            chat_session = ChatSession.objects.create()
            request.session['chat_session_id'] = str(chat_session.session_id)
    else:
        chat_session = ChatSession.objects.create()
        request.session['chat_session_id'] = str(chat_session.session_id)

    return render(request, 'core/chat.html', {
        'session': chat_session
    })


@csrf_exempt
@require_http_methods(["POST"])
def chat_message(request):
    """Handle chat message and get AI response"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')

        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Get or create session
        chat_session = ChatSession.objects.get(session_id=session_id)

        # Add user message
        chat_session.add_message('user', message)

        # Get conversation history
        messages = chat_session.get_recent_messages(limit=10)

        # Prepare messages for AI
        ai_messages = [{'role': msg['role'], 'content': msg['content']} for msg in messages]

        # Get AI response
        response = asyncio.run(
            ai_provider.chat(ai_messages, max_tokens=1000)
        )

        # Add AI response to session
        chat_session.add_message('assistant', response)

        return JsonResponse({
            'success': True,
            'response': response,
            'session_id': str(chat_session.session_id)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def generate(request):
    """Article generation interface"""
    return render(request, 'core/generate.html')


@csrf_exempt
@require_http_methods(["POST"])
def generate_article(request):
    """Generate article using AI"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '').strip()
        article_type = data.get('type', 'review')
        length = data.get('length', 'medium')
        style = data.get('style', 'academic')

        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        # Find relevant context articles
        context_articles = []
        if ArticleEmbedding.objects.exists():
            try:
                similar = asyncio.run(embedding_service.search_similar(topic, limit=3))
                context_articles = [
                    f"{art.title}: {art.abstract or 'No abstract'}"
                    for art, score in similar
                ]
            except:
                pass

        # Generate article
        start_time = time.time()
        result = asyncio.run(
            ai_provider.generate_article(
                topic=topic,
                article_type=article_type,
                length=length,
                style=style,
                context_articles=context_articles
            )
        )
        generation_time = time.time() - start_time

        # Save generated article
        generated = GeneratedArticle.objects.create(
            title=result['title'],
            content=result['content'],
            topic=topic,
            article_type=article_type,
            length=length,
            style=style,
            generation_time_seconds=generation_time
        )

        return JsonResponse({
            'success': True,
            'article': {
                'id': generated.id,
                'title': result['title'],
                'content': result['content'],
                'generation_time': round(generation_time, 2)
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def analytics(request):
    """Analytics dashboard"""
    top_searches = SearchQuery.objects.values('query_text').distinct()[:10]
    recent_generations = GeneratedArticle.objects.all()[:10]

    return render(request, 'core/analytics.html', {
        'top_searches': top_searches,
        'recent_generations': recent_generations
    })
