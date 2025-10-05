from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Article, ChatSession, SearchQuery, GeneratedArticle, ArticleEmbedding, LiteratureReview
from .services.ai_providers import ai_provider
from .services.embeddings import embedding_service
from .services.context_guard import context_guard
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
            # Enhanced text search with multiple fields
            from django.db.models import Q, Count

            queryset = Article.objects.filter(
                Q(title__icontains=query) |
                Q(abstract__icontains=query) |
                Q(authors__icontains=query)
            )

            # Optional year filter
            year_filter = request.GET.get('year', '')
            if year_filter:
                queryset = queryset.filter(publication_date__year=year_filter)

            # Order by views (most popular first)
            results = queryset.order_by('-views_count', '-publication_date')[:50]

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


@require_http_methods(["GET"])
def get_article_json(request, article_id):
    """Get article data as JSON for in-app viewer"""
    article = get_object_or_404(Article, id=article_id)
    article.increment_views()

    # Get similar articles if embeddings exist
    similar_articles = []
    if hasattr(article, 'embedding'):
        try:
            similar_results = asyncio.run(
                embedding_service.search_similar(article.title, limit=5)
            )
            similar_articles = [
                {
                    'id': art.id,
                    'title': art.title,
                    'abstract': art.abstract or '',
                    'pmc_id': art.pmc_id
                }
                for art, score in similar_results if art.id != article.id
            ][:5]
        except:
            pass

    return JsonResponse({
        'id': article.id,
        'title': article.title,
        'abstract': article.abstract or '',
        'content': article.content or '',
        'pmc_id': article.pmc_id or '',
        'url': article.url,
        'authors': article.authors,
        'keywords': article.keywords,
        'publication_date': article.publication_date.strftime('%B %d, %Y') if article.publication_date else None,
        'views_count': article.views_count,
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
        'session': chat_session,
        'messages_json': json.dumps(chat_session.messages)  # Serialize messages for JavaScript
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

        # Validate context - check if question is relevant to space biology
        is_valid, validation_message = asyncio.run(
            context_guard.validate_context(message)
        )

        if not is_valid:
            # Question is off-topic, return polite redirect
            chat_session.add_message('assistant', validation_message)
            return JsonResponse({
                'success': True,
                'response': validation_message,
                'session_id': str(chat_session.session_id),
                'off_topic': True
            })

        # Search for relevant articles to provide context
        context_articles = []
        try:
            # Try semantic search first if embeddings exist
            if ArticleEmbedding.objects.exists():
                similar = asyncio.run(embedding_service.search_similar(message, limit=3))
                context_articles = [
                    f"**{art.title}** (Year: {art.publication_date.year if art.publication_date else 'N/A'})\n"
                    f"Authors: {art.authors or 'N/A'}\n"
                    f"Abstract: {(art.abstract or 'No abstract')[:300]}..."
                    for art, score in similar if score > 0.5  # Only include relevant matches
                ]
            else:
                # Fallback to simple keyword search
                keywords = message.lower().split()[:5]
                articles = Article.objects.filter(
                    Q(title__icontains=keywords[0]) |
                    Q(abstract__icontains=keywords[0]) if keywords else Q()
                )[:3]
                context_articles = [
                    f"**{art.title}** (Year: {art.publication_date.year if art.publication_date else 'N/A'})\n"
                    f"Authors: {art.authors or 'N/A'}\n"
                    f"Abstract: {(art.abstract or 'No abstract')[:300]}..."
                    for art in articles
                ]
        except Exception as e:
            # If search fails, continue without context
            import logging
            logging.error(f"Article search failed: {e}")

        # Get conversation history
        messages = chat_session.get_recent_messages(limit=10)

        # Prepare messages for AI
        ai_messages = [{'role': msg['role'], 'content': msg['content']} for msg in messages]

        # Get AI response with article context
        response = asyncio.run(
            ai_provider.chat(
                ai_messages,
                max_tokens=1000,
                context_articles=context_articles if context_articles else None
            )
        )

        # Add AI response to session
        chat_session.add_message('assistant', response)

        return JsonResponse({
            'success': True,
            'response': response,
            'session_id': str(chat_session.session_id),
            'sources_used': len(context_articles)
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
    """Synthesize research article from database articles (NOT AI generation)"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '').strip()
        article_type = data.get('type', 'review')
        length = data.get('length', 'medium')
        style = data.get('style', 'academic')

        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        # Validate topic is relevant to space biology
        is_valid, validation_message = asyncio.run(
            context_guard.validate_context(topic)
        )

        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': 'Topic must be related to space biology research. ' + validation_message
            }, status=400)

        # Find relevant source articles - REQUIRED for synthesis
        context_articles = []
        article_count = 0

        try:
            # Try semantic search first (more accurate)
            if ArticleEmbedding.objects.exists():
                similar = asyncio.run(embedding_service.search_similar(topic, limit=5))
                context_articles = [
                    f"**{art.title}**\n"
                    f"Year: {art.publication_date.year if art.publication_date else 'N/A'}\n"
                    f"Authors: {art.authors or 'N/A'}\n"
                    f"Abstract: {art.abstract or 'No abstract available'}\n"
                    f"Relevance: {score:.2f}"
                    for art, score in similar if score > 0.3
                ]
                article_count = len(context_articles)

            # Fallback to keyword search if no embeddings
            if not context_articles:
                keywords = topic.lower().split()[:3]
                q_filter = Q()
                for keyword in keywords:
                    q_filter |= Q(title__icontains=keyword) | Q(abstract__icontains=keyword)

                articles = Article.objects.filter(q_filter).distinct()[:5]
                context_articles = [
                    f"**{art.title}**\n"
                    f"Year: {art.publication_date.year if art.publication_date else 'N/A'}\n"
                    f"Authors: {art.authors or 'N/A'}\n"
                    f"Abstract: {art.abstract or 'No abstract available'}"
                    for art in articles
                ]
                article_count = len(context_articles)

        except Exception as e:
            import logging
            logging.error(f"Article search failed: {e}")

        # Check if we have enough source articles
        if not context_articles or article_count == 0:
            return JsonResponse({
                'success': False,
                'error': f'No relevant research articles found for "{topic}". '
                        f'This synthesis tool requires existing research articles from our database. '
                        f'Try a different topic or broader search terms related to space biology.'
            }, status=404)

        # Synthesize research article from sources
        start_time = time.time()
        result = asyncio.run(
            ai_provider.synthesize_research(
                topic=topic,
                article_type=article_type,
                length=length,
                style=style,
                context_articles=context_articles
            )
        )
        synthesis_time = time.time() - start_time

        # Save synthesized article
        generated = GeneratedArticle.objects.create(
            title=result['title'],
            content=result['content'],
            topic=topic,
            article_type=article_type,
            length=length,
            style=style,
            generation_time_seconds=synthesis_time
        )

        return JsonResponse({
            'success': True,
            'article': {
                'id': generated.id,
                'title': result['title'],
                'content': result['content'],
                'synthesis_time': round(synthesis_time, 2),
                'source_articles': article_count,
                'note': f'This synthesis is based on {article_count} research articles from our database.'
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


def literature_review(request):
    """Literature review interface"""
    recent_reviews = LiteratureReview.objects.all()[:10]

    return render(request, 'core/literature_review.html', {
        'recent_reviews': recent_reviews
    })


@csrf_exempt
@require_http_methods(["POST"])
def generate_literature_review(request):
    """Generate comprehensive literature review on a topic"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '').strip()
        max_articles = data.get('max_articles', 20)

        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        start_time = time.time()

        # Step 1: Find relevant articles (semantic search if available)
        relevant_articles = []
        if ArticleEmbedding.objects.exists():
            try:
                similar = asyncio.run(
                    embedding_service.search_similar(topic, limit=max_articles)
                )
                relevant_articles = [art for art, score in similar if score > 0.6]
            except:
                pass

        # Fallback to simple search
        if not relevant_articles:
            relevant_articles = Article.objects.filter(
                Q(title__icontains=topic) |
                Q(abstract__icontains=topic) |
                Q(content__icontains=topic)
            )[:max_articles]

        if not relevant_articles:
            return JsonResponse({
                'error': f'No articles found on topic: {topic}'
            }, status=404)

        # Step 2: Extract key information from articles
        articles_data = []
        for article in relevant_articles:
            articles_data.append({
                'title': article.title,
                'abstract': article.abstract or 'No abstract available',
                'content': (article.content or '')[:1500],  # Limit content length
                'authors': article.authors[:3] if article.authors else [],
                'year': article.publication_date.year if article.publication_date else 'N/A',
                'pmc_id': article.pmc_id or 'N/A'
            })

        # Step 3: Generate structured literature review using AI
        prompt = f"""Generate a comprehensive literature review on: {topic}

Based on {len(articles_data)} scientific articles from NASA's space biology research.

Articles summary:
{json.dumps(articles_data[:10], indent=2)}

Generate a structured review with these sections:

## Introduction
Brief overview of the topic and its importance in space biology research.

## Current Findings
Synthesize the main findings from the articles. Group similar findings together.
Include specific citations like (Author et al., Year).

## Controversies & Research Gaps
Identify any conflicting findings or areas needing more research.

## Future Directions
Based on the research, what are the promising future directions?

## Conclusion
Summarize key takeaways.

Format with markdown. Be specific and cite studies appropriately."""

        # Call AI provider
        review_content = asyncio.run(
            ai_provider.generate(
                prompt=prompt,
                max_tokens=3000
            )
        )

        generation_time = time.time() - start_time

        # Step 4: Parse sections (basic parsing)
        sections = {
            'introduction': '',
            'current_findings': '',
            'controversies': '',
            'future_directions': '',
            'conclusion': ''
        }

        # Simple section extraction
        current_section = None
        for line in review_content.split('\n'):
            if '## Introduction' in line:
                current_section = 'introduction'
            elif '## Current Findings' in line:
                current_section = 'current_findings'
            elif '## Controversies' in line or '## Research Gaps' in line:
                current_section = 'controversies'
            elif '## Future Directions' in line:
                current_section = 'future_directions'
            elif '## Conclusion' in line:
                current_section = 'conclusion'
            elif current_section and line.strip():
                sections[current_section] += line + '\n'

        # Step 5: Generate citations in APA format
        citations = []
        for art in relevant_articles:
            authors_str = ', '.join(art.authors[:3]) if art.authors else 'Unknown'
            year = art.publication_date.year if art.publication_date else 'n.d.'
            citations.append({
                'authors': authors_str,
                'year': year,
                'title': art.title,
                'pmc_id': art.pmc_id or 'N/A',
                'url': art.url
            })

        # Step 6: Save literature review
        lit_review = LiteratureReview.objects.create(
            topic=topic,
            introduction=sections['introduction'],
            current_findings=sections['current_findings'],
            controversies=sections['controversies'],
            future_directions=sections['future_directions'],
            conclusion=sections['conclusion'],
            full_review=review_content,
            articles_count=len(relevant_articles),
            citations=citations,
            generation_time_seconds=generation_time
        )

        # Add source articles
        lit_review.source_articles.set(relevant_articles)

        return JsonResponse({
            'success': True,
            'review': {
                'id': lit_review.id,
                'topic': topic,
                'full_review': review_content,
                'sections': sections,
                'citations': citations,
                'articles_count': len(relevant_articles),
                'generation_time': round(generation_time, 2)
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Luma Kids Chatbot views

def luma(request):
    """Kids-friendly chatbot page for Luma persona"""
    # Create or get Luma chat session (separate from adult chat)
    session_id = request.session.get('luma_session_id')

    if session_id:
        try:
            chat_session = ChatSession.objects.get(session_id=session_id, is_active=True)
        except ChatSession.DoesNotExist:
            chat_session = ChatSession.objects.create()
            request.session['luma_session_id'] = str(chat_session.session_id)
    else:
        chat_session = ChatSession.objects.create()
        request.session['luma_session_id'] = str(chat_session.session_id)

    # Initialize simple progress tracking in Django session
    if 'luma_score' not in request.session:
        request.session['luma_score'] = 0
    if 'luma_badges' not in request.session:
        request.session['luma_badges'] = []

    # Seed a starter message if this is a fresh session
    if len(chat_session.messages) == 0:
        start_message = (
            "👋 Hi space explorer! I'm Luma, your intergalactic guide 🪐.\n"
            "I have lots of games for you today! What do you want to do?\n\n"
            "1️⃣ Bioplant Mission 🌱: discover how plants survive on a space station!\n"
            "2️⃣ Body in Microgravity 🧑‍🚀: explore what happens to your body in space!\n"
            "3️⃣ Cosmic Quiz 🧬: a challenge to test your science memory!\n\n"
            "Choose your adventure by typing the number or the game name 🚀"
        )
        chat_session.add_message('assistant', start_message)

    return render(request, 'core/luma.html', {
        'session': chat_session,
        'messages_json': json.dumps(chat_session.messages),
        'luma_score': request.session.get('luma_score', 0),
        'luma_badges': request.session.get('luma_badges', []),
    })


@csrf_exempt
@require_http_methods(["POST"])
def luma_message(request):
    """Handle kids chatbot message via Luma persona and return AI response"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')

        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Load session
        chat_session = ChatSession.objects.get(session_id=session_id)

        # Add child message
        chat_session.add_message('user', message)

        # Build kid-friendly, grounded context from our articles
        context_articles = []
        try:
            if ArticleEmbedding.objects.exists():
                similar = asyncio.run(embedding_service.search_similar(message, limit=3))
                context_articles = [
                    (
                        f"• {art.title}\n"
                        f"Summary: {(art.abstract or 'No abstract')[:200]}...\n"
                        f"Link: {art.url}"
                    )
                    for art, score in similar if score > 0.5
                ]
            else:
                keywords = message.lower().split()[:5]
                articles = Article.objects.filter(
                    Q(title__icontains=keywords[0]) |
                    Q(abstract__icontains=keywords[0]) if keywords else Q()
                )[:3]
                context_articles = [
                    (
                        f"• {art.title}\n"
                        f"Summary: {(art.abstract or 'No abstract')[:200]}...\n"
                        f"Link: {art.url}"
                    )
                    for art in articles
                ]
        except Exception:
            # If search fails, continue without context
            context_articles = []

        # Recent conversation history
        messages_hist = chat_session.get_recent_messages(limit=10)
        ai_messages = [{'role': m['role'], 'content': m['content']} for m in messages_hist]

        # Luma persona system prompt (English, age-appropriate, game-based)
        luma_system_prompt = """You are Luma, a playful learning companion for kids aged 7–12.
Domain: space biology 🌌🧬.
Goal: teach by playing (quizzes, riddles, short stories, true/false, mini-challenges).

Style & rules:
- Joyful, empathetic, engaging tone 🎈 (use emojis).
- SHORT replies: 1–3 sentences, then a question or a choice.
- Vary formats: quiz, riddle, true/false, mini-adventure.
- Celebrate success often: “Great job, young scientist!” ✅
- Use kid-friendly words; simplify concepts with concrete examples.
- If off-topic, gently redirect to space biology.
- Frequently offer activity choices (e.g., 1, 2, 3).
- You may award badges: “Lunar Biologist 🌕”, “Plant Hero 🌱”, etc.

Scientific content:
- ONLY use information from the provided context (articles) or simple, safe space-biology facts.
- Rephrase for kids; do not invent studies.
- You may provide “Learn more” with a link (if present).

Game flow:
- If the child picks “Bioplant Mission”, ask a simple question (e.g., why do roots get confused in microgravity?) and propose 3 fun options (a/b/c).
- If correct, celebrate and add a tiny challenge or a vivid mental image.
- Keep the pace: offer to continue the mission or try another game.
"""

        # Get AI response with Luma persona
        response = asyncio.run(
            ai_provider.chat(
                ai_messages,
                max_tokens=800,
                context_articles=context_articles if context_articles else None,
                system_prompt=luma_system_prompt
            )
        )

        # Add AI response
        chat_session.add_message('assistant', response)

        # Naive score/badge tracking (heuristics; can be improved)
        score_inc = 1 if ('✅' in response) or ('Bravo' in response) else 0
        request.session['luma_score'] = request.session.get('luma_score', 0) + score_inc

        badges = request.session.get('luma_badges', [])
        if ('badge' in response.lower()) and ('lunaire' in response.lower()) and ('Biologiste Lunaire' not in badges):
            badges.append('Biologiste Lunaire 🌕')
        request.session['luma_badges'] = badges

        return JsonResponse({
            'success': True,
            'response': response,
            'session_id': str(chat_session.session_id),
            'persona': 'luma',
            'score': request.session['luma_score'],
            'badges': request.session['luma_badges']
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# Knowledge Graph and Experiment Scenario features

def knowledge_graph(request):
    """Interactive knowledge graph page to explore article connections"""
    # Provide some articles for quick selection; frontend can still accept manual input
    articles = Article.objects.all()[:50]

    # Data readiness metrics to align UI with project data sources
    stats_total_articles = Article.objects.count()
    stats_embeddings = ArticleEmbedding.objects.count()

    return render(request, 'core/knowledge_graph.html', {
        'articles': articles,
        'stats_total_articles': stats_total_articles,
        'stats_embeddings': stats_embeddings,
    })


@require_http_methods(["GET"])
def generate_knowledge_graph(request):
    """
    Build a knowledge graph for a selected article.
    Nodes: articles, authors, keywords
    Edges: similarity(article↔article), authored(author↔article), tagged(keyword↔article)
    Insights: top authors, top keywords
    """
    try:
        article_id = request.GET.get('article_id')
        if not article_id:
            return JsonResponse({'success': False, 'error': 'article_id is required'}, status=400)

        article = get_object_or_404(Article, id=article_id)

        # Initialize graph
        nodes = []
        edges = []

        def add_node(node_id, label, node_type, extra=None):
            if extra is None:
                extra = {}
            nodes.append({
                'id': node_id,
                'label': label,
                'type': node_type,
                **extra
            })

        def add_edge(source, target, label, edge_type, extra=None):
            if extra is None:
                extra = {}
            edges.append({
                'source': source,
                'target': target,
                'label': label,
                'type': edge_type,
                **extra
            })

        # Main article node
        main_id = f"article:{article.id}"
        add_node(main_id, article.title, 'article', {
            'pmc_id': article.pmc_id,
            'url': article.url
        })

        # Authors and keywords of main article
        for author in (article.authors or [])[:10]:
            author_id = f"author:{author}"
            # Avoid duplicates with a simple presence check
            if not any(n['id'] == author_id for n in nodes):
                add_node(author_id, author, 'author')
            add_edge(author_id, main_id, 'authored', 'authored')

        for kw in (article.keywords or [])[:10]:
            kw_id = f"keyword:{kw}"
            if not any(n['id'] == kw_id for n in nodes):
                add_node(kw_id, kw, 'keyword')
            add_edge(kw_id, main_id, 'tagged', 'tagged')

        # Similarity-based related articles via embeddings if available
        similar_results = []
        try:
            if ArticleEmbedding.objects.exists():
                similar_results = asyncio.run(
                    embedding_service.search_similar(article.title, limit=15)
                )
        except Exception:
            similar_results = []

        # Fallback: keyword-based search if embeddings not available or failed
        if not similar_results:
            try:
                words = (article.title or '').lower().split()[:3]
                q = Q()
                for w in words:
                    q |= Q(title__icontains=w) | Q(abstract__icontains=w)
                fallback_articles = Article.objects.filter(q).exclude(id=article.id)[:10]
                similar_results = [(a, 0.3) for a in fallback_articles]
            except Exception:
                similar_results = []

        # Build graph from similar results
        author_counts = {}
        keyword_counts = {}

        for sim_article, score in similar_results:
            if sim_article.id == article.id:
                continue
            sid = f"article:{sim_article.id}"
            if not any(n['id'] == sid for n in nodes):
                add_node(sid, sim_article.title, 'article', {
                    'pmc_id': sim_article.pmc_id,
                    'url': sim_article.url,
                    'publication_year': sim_article.publication_date.year if sim_article.publication_date else None
                })

            # Similarity edge
            add_edge(main_id, sid, f"similarity {score:.2f}", 'similarity', {'weight': score})

            # Authors and keywords nodes/edges
            for author in (sim_article.authors or [])[:10]:
                author_counts[author] = author_counts.get(author, 0) + 1
                aid = f"author:{author}"
                if not any(n['id'] == aid for n in nodes):
                    add_node(aid, author, 'author')
                add_edge(aid, sid, 'authored', 'authored')

            for kw in (sim_article.keywords or [])[:10]:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
                kid = f"keyword:{kw}"
                if not any(n['id'] == kid for n in nodes):
                    add_node(kid, kw, 'keyword')
                add_edge(kid, sid, 'tagged', 'tagged')

        # Simple insights: top authors and keywords across the neighborhood
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return JsonResponse({
            'success': True,
            'graph': {
                'nodes': nodes,
                'edges': edges
            },
            'insights': {
                'top_authors': [{'name': a, 'count': c} for a, c in top_authors],
                'top_keywords': [{'keyword': k, 'count': c} for k, c in top_keywords]
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def experiment_extractor(request):
    """Experiment scenario extraction page"""
    # Provide a few articles for selection convenience
    articles = Article.objects.all()[:50]
    return render(request, 'core/experiment_extractor.html', {
        'articles': articles
    })


@csrf_exempt
@require_http_methods(["POST"])
def extract_scenarios(request):
    """
    Extract structured experimental scenarios from a selected article.
    Returns a standardized JSON with steps, variables, results, conclusions, and cross-study suggestions.
    """
    try:
        data = json.loads(request.body)
        article_id = str(data.get('article_id', '')).strip()
        if not article_id:
            return JsonResponse({'success': False, 'error': 'article_id is required'}, status=400)

        article = get_object_or_404(Article, id=article_id)

        # Build input text (limit sizes to keep prompt reasonable)
        title = article.title or ''
        abstract = (article.abstract or '')[:2000]
        content_snip = (article.content or '')[:4000]

        prompt = f"""Extract standardized experimental scenarios from the following scientific article.

Article Title: {title}

Abstract:
{abstract}

Content (snippet):
{content_snip}

Output STRICTLY in JSON with this schema:
{{
  "scenarios": [
    {{
      "title": "short scenario title",
      "objective": "goal of the experiment",
      "steps": ["step 1", "step 2", "step 3"],
      "variables": ["independent variables", "dependent variables", "controls"],
      "methods": ["key methods used"],
      "results": ["main results"],
      "conclusions": ["key conclusions"]
    }}
  ],
  "cross_study_suggestions": [
    {{
      "idea": "combine scenario X from this article with scenario Y from related articles",
      "rationale": "why this combination is promising",
      "hypothesis": "testable hypothesis"
    }}
  ]
}}

Rules:
- Use only information inferable from this article excerpt; do not invent studies.
- Keep steps concise and actionable.
- If data is missing, include placeholders like "unknown".
"""

        # Ask AI provider to produce structured JSON
        raw = asyncio.run(ai_provider.generate(prompt=prompt, max_tokens=1500))

        # Try to parse JSON; if parsing fails, return raw text for inspection
        try:
            parsed = json.loads(raw)
            return JsonResponse({'success': True, 'data': parsed})
        except Exception:
            return JsonResponse({'success': True, 'data_raw': raw})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
