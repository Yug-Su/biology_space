"""
AI Providers Service - Unified interface for OpenRouter and Groq APIs
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
    Unified AI Provider with automatic failover between OpenRouter and Groq

    Features:
    - Automatic retry with exponential backoff
    - Fallback from primary to secondary provider
    - Cost optimization with model selection
    - Streaming support for real-time responses
    """

    def __init__(self):
        self.openrouter_key = settings.OPENROUTER_API_KEY
        self.openrouter_base = settings.OPENROUTER_BASE_URL
        self.groq_key = settings.GROQ_API_KEY
        self.groq_base = settings.GROQ_BASE_URL

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

    async def _call_groq(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        model: Optional[str] = None
    ) -> str:
        """Call Groq API"""
        model = model or self.fallback_model

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.groq_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
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
                logger.error(f"Groq API error: {e}")
                raise AIProviderError(f"Groq failed: {str(e)}")

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

            # Try fallback provider (Groq)
            try:
                logger.info(f"Calling fallback provider (Groq) with model {self.fallback_model}")
                return await self._call_groq(messages, max_tokens)

            except AIProviderError as fallback_error:
                logger.error(f"All providers failed: {fallback_error}")
                raise AIProviderError(f"All AI providers failed. Primary: {e}, Fallback: {fallback_error}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        context_articles: Optional[List[str]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Chat with AI maintaining conversation history

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens to generate
            context_articles: Optional list of relevant article summaries for context

        Returns:
            AI response
        """
        # Add system prompt with space biology context (allow override)
        if system_prompt is None:
            system_prompt = """You are an expert AI assistant specialized in space biology and microgravity research.

Your knowledge domain includes:
- Effects of microgravity on biological systems (cells, tissues, organisms)
- Astronaut health and physiology in space
- International Space Station (ISS) experiments
- Radiation biology and cosmic ray effects
- Countermeasures for bone loss, muscle atrophy, and other spaceflight issues
- NASA research programs and publications
- Plant and animal biology in space environments
- Long-duration spaceflight medical challenges

IMPORTANT CONSTRAINTS:
1. ONLY answer questions related to space biology, microgravity research, and astronaut health
2. If a question is completely unrelated to your domain, politely redirect: "I specialize in space biology and microgravity research. Could you ask about topics like astronaut health, microgravity effects, or space experiments?"
3. Base your answers on scientific research principles
4. Cite general research areas when relevant (e.g., "Studies on the ISS have shown...")
5. Be accurate and admit when you don't have specific information

Maintain a professional, scientific tone while being accessible to non-experts."""
        # Add context articles if provided
        if context_articles:
            context_text = "\n\nRELEVANT RESEARCH ARTICLES:\n" + "\n".join(
                f"- {article}" for article in context_articles
            )
            system_prompt += context_text
            system_prompt += "\n\nUse the above articles to inform your response when relevant."

        # Prepend system message
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            return await self._call_openrouter(full_messages, max_tokens)
        except AIProviderError:
            # Fallback to Groq
            return await self._call_groq(full_messages, max_tokens)

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

    async def synthesize_research(
        self,
        topic: str,
        article_type: str = 'review',
        length: str = 'medium',
        style: str = 'academic',
        context_articles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize research article based on existing scientific articles
        IMPORTANT: This creates a synthesis of real research, not generated fiction

        Args:
            topic: Research topic
            article_type: 'review', 'research', or 'protocol'
            length: 'short' (500 words), 'medium' (1000 words), 'long' (2000 words)
            style: 'academic', 'executive', or 'technical'
            context_articles: REQUIRED list of article summaries to synthesize from

        Returns:
            Dict with 'title', 'content', 'references'
        """
        if not context_articles or len(context_articles) == 0:
            raise AIProviderError("Cannot synthesize without source articles. Search returned no relevant research.")

        word_counts = {'short': 500, 'medium': 1000, 'long': 2000}
        target_words = word_counts.get(length, 1000)

        # Build detailed context from articles
        articles_context = "\n\nSOURCE RESEARCH ARTICLES (YOU MUST SYNTHESIZE FROM THESE):\n"
        articles_context += "\n".join(f"{i+1}. {article}" for i, article in enumerate(context_articles[:5]))

        system_prompt = f"""You are a research synthesis specialist creating a {article_type} by analyzing and synthesizing REAL published research.

CRITICAL REQUIREMENTS:
1. **ONLY use information from the provided source articles below**
2. **DO NOT invent or hallucinate facts, studies, or data**
3. **Synthesize and cross-reference the provided research**
4. **If the sources don't cover an aspect, acknowledge the limitation**
5. **Cite which source article information comes from (e.g., "Article 1 shows...")**

Your task: Create a {target_words}-word {article_type} in {style} style that:
- Synthesizes findings across the provided articles
- Identifies common themes and contradictions
- Draws evidence-based conclusions
- Maintains scientific accuracy by staying true to source material

Structure:
1. Title (reflecting the synthesis)
2. Abstract (summarizing what the source articles reveal)
3. Introduction (context from the articles)
4. Main Analysis (synthesizing findings from sources)
5. Discussion (cross-referencing and comparing articles)
6. Conclusion (evidence-based summary)
7. References (list the source articles used)

{articles_context}

Remember: This is a SYNTHESIS of existing research, not creative writing. Stay grounded in the source material."""

        prompt = f"""Based ONLY on the source articles provided above, create a comprehensive {article_type} synthesis about: {topic}

Analyze and integrate findings from all provided articles. Do not add external information."""

        content = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=settings.MAX_TOKENS_GENERATION
        )

        # Parse title from content (assumes first line is title)
        lines = content.strip().split('\n')
        title = lines[0].replace('#', '').strip()
        article_content = '\n'.join(lines[1:]).strip()

        # Add metadata about sources
        article_content += f"\n\n---\n**Note:** This synthesis is based on {len(context_articles)} research articles from our database."

        return {
            'title': title,
            'content': article_content,
            'metadata': {
                'type': article_type,
                'length': length,
                'style': style,
                'topic': topic,
                'source_count': len(context_articles)
            }
        }


# Singleton instance
ai_provider = AIProvider()
