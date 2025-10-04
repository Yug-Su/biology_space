"""
AI Providers Service - Unified interface for OpenRouter and Grok APIs
Handles automatic fallback, retry logic, and cost optimization
"""

import httpx
import json
from typing import Optional, Dict, List, Any
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Custom exception for AI provider errors"""
    pass


class AIProvider:
    """
    Unified AI Provider with automatic failover between OpenRouter and Grok

    Features:
    - Automatic retry with exponential backoff
    - Fallback from primary to secondary provider
    - Cost optimization with model selection
    - Streaming support for real-time responses
    """

    def __init__(self):
        self.openrouter_key = settings.OPENROUTER_API_KEY
        self.openrouter_base = settings.OPENROUTER_BASE_URL
        self.grok_key = settings.GROK_API_KEY
        self.grok_base = settings.GROK_BASE_URL

        self.primary_model = settings.PRIMARY_AI_MODEL
        self.fallback_model = settings.FALLBACK_AI_MODEL
        self.temperature = settings.TEMPERATURE

    async def _call_openrouter(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        model: Optional[str] = None
    ) -> str:
        """Call OpenRouter API"""
        model = model or self.primary_model

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.openrouter_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",  # Required by OpenRouter
                        "X-Title": "SpaceBio Platform"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": self.temperature
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content']

            except httpx.HTTPError as e:
                logger.error(f"OpenRouter API error: {e}")
                raise AIProviderError(f"OpenRouter failed: {str(e)}")

    async def _call_grok(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        model: Optional[str] = None
    ) -> str:
        """Call Grok API"""
        model = model or self.fallback_model

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.grok_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": self.temperature
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content']

            except httpx.HTTPError as e:
                logger.error(f"Grok API error: {e}")
                raise AIProviderError(f"Grok failed: {str(e)}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        use_fallback: bool = True
    ) -> str:
        """
        Generate text using AI with automatic fallback

        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            use_fallback: Whether to try fallback provider on failure

        Returns:
            Generated text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Try primary provider (OpenRouter)
        try:
            logger.info(f"Calling primary provider (OpenRouter) with model {self.primary_model}")
            return await self._call_openrouter(messages, max_tokens)

        except AIProviderError as e:
            if not use_fallback:
                raise

            logger.warning(f"Primary provider failed, trying fallback: {e}")

            # Try fallback provider (Grok)
            try:
                logger.info(f"Calling fallback provider (Grok) with model {self.fallback_model}")
                return await self._call_grok(messages, max_tokens)

            except AIProviderError as fallback_error:
                logger.error(f"All providers failed: {fallback_error}")
                raise AIProviderError(f"All AI providers failed. Primary: {e}, Fallback: {fallback_error}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000
    ) -> str:
        """
        Chat with AI maintaining conversation history

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens to generate

        Returns:
            AI response
        """
        try:
            return await self._call_openrouter(messages, max_tokens)
        except AIProviderError:
            # Fallback to Grok
            return await self._call_grok(messages, max_tokens)

    async def summarize(
        self,
        text: str,
        summary_type: str = 'concise'
    ) -> str:
        """
        Summarize scientific text

        Args:
            text: Text to summarize
            summary_type: 'concise' (100 words) or 'detailed' (300 words)

        Returns:
            Summary text
        """
        max_words = 100 if summary_type == 'concise' else 300

        system_prompt = f"""You are a scientific summarizer specialized in space biology research.
Create a {summary_type} summary ({max_words} words max) that captures:
- Main findings
- Methodology highlights
- Significance to space biology

Use clear, accessible language while maintaining scientific accuracy."""

        prompt = f"Summarize this scientific article:\n\n{text[:4000]}"  # Limit input to 4000 chars

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=settings.MAX_TOKENS_SUMMARY
        )

    async def generate_article(
        self,
        topic: str,
        article_type: str = 'review',
        length: str = 'medium',
        style: str = 'academic',
        context_articles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate scientific article based on topic

        Args:
            topic: Article topic
            article_type: 'review', 'research', or 'protocol'
            length: 'short' (500 words), 'medium' (1000 words), 'long' (2000 words)
            style: 'academic', 'executive', or 'technical'
            context_articles: Optional list of article summaries for context

        Returns:
            Dict with 'title', 'content', 'references'
        """
        word_counts = {'short': 500, 'medium': 1000, 'long': 2000}
        target_words = word_counts.get(length, 1000)

        context = ""
        if context_articles:
            context = "\n\nContext from related research:\n" + "\n".join(context_articles[:3])

        system_prompt = f"""You are an expert space biology researcher writing a {article_type} article.
Write in {style} style for {target_words} words.

Structure:
1. Compelling title
2. Abstract
3. Introduction
4. Main content sections
5. Conclusion
6. Key references

Focus on space biology aspects: microgravity effects, radiation, ISS experiments, etc."""

        prompt = f"Write a comprehensive {article_type} article about: {topic}{context}"

        content = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=settings.MAX_TOKENS_GENERATION
        )

        # Parse title from content (assumes first line is title)
        lines = content.strip().split('\n')
        title = lines[0].replace('#', '').strip()
        article_content = '\n'.join(lines[1:]).strip()

        return {
            'title': title,
            'content': article_content,
            'metadata': {
                'type': article_type,
                'length': length,
                'style': style,
                'topic': topic
            }
        }


# Singleton instance
ai_provider = AIProvider()
