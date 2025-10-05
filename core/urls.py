from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('chat/', views.chat, name='chat'),
    path('generate/', views.generate, name='generate'),
    path('analytics/', views.analytics, name='analytics'),
    path('literature-review/', views.literature_review, name='literature_review'),

    # Article details
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),

    # API endpoints
    path('api/article/<int:article_id>/', views.get_article_json, name='get_article_json'),
    path('api/article/<int:article_id>/summarize/', views.summarize_article, name='summarize_article'),
    path('api/chat/message/', views.chat_message, name='chat_message'),
    path('api/generate/', views.generate_article, name='generate_article'),
    path('api/literature-review/', views.generate_literature_review, name='generate_literature_review'),
]
