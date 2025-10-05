"""
Context Guard Service - Validates queries are relevant to space biology research
Filters out off-topic questions and ensures AI stays within domain expertise
"""

import httpx
from typing import Tuple
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ContextGuard:
    """
    Guards against off-topic queries to ensure AI responses stay focused
    on space biology, microgravity research, and NASA-related topics.
    """

    # Keywords that indicate space biology context
    SPACE_BIOLOGY_KEYWORDS = [
        'space', 'microgravity', 'astronaut', 'iss', 'nasa', 'orbit',
        'radiation', 'cosmic', 'weightless', 'spaceflight', 'mars',
        'moon', 'bone', 'muscle', 'cell', 'biology', 'gravity',
        'adaptation', 'countermeasure', 'mission', 'research',
        'experiment', 'station', 'crew', 'physiology', 'health',
        'medical', 'science', 'tissue', 'organism', 'gene', 'protein',
        'immune', 'cardiovascular', 'osteoporosis', 'atrophy'
    ]

    def __init__(self):
        self.openrouter_key = settings.OPENROUTER_API_KEY
        self.openrouter_base = settings.OPENROUTER_BASE_URL
        self.groq_key = settings.GROQ_API_KEY
        self.groq_base = settings.GROQ_BASE_URL

    def quick_keyword_check(self, query: str) -> bool:
        """
        Fast keyword-based check before using AI validation
        Returns True if query contains space biology keywords
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.SPACE_BIOLOGY_KEYWORDS)

    async def validate_context(self, query: str) -> Tuple[bool, str]:
        """
        Validate if query is relevant to space biology research

        Args:
            query: User's question or topic

        Returns:
            Tuple of (is_valid, message)
            - is_valid: True if query is relevant to space biology
            - message: Explanation or polite redirect if not relevant
        """
        # First do quick keyword check
        if self.quick_keyword_check(query):
            return True, ""

        # If no obvious keywords, use AI to classify
        try:
            is_relevant = await self._ai_classify_query(query)

            if is_relevant:
                return True, ""
            else:
                polite_message = (
                    "I'm specialized in space biology and microgravity research. "
                    "Your question seems outside this domain. I focus on topics like: "
                    "astronaut health, microgravity effects on organisms, ISS experiments, "
                    "radiation biology, and countermeasures for spaceflight. "
                    "Could you rephrase your question to relate to space biology research?"
                )
                return False, polite_message

        except Exception as e:
            logger.error(f"Context validation error: {e}")
            # On error, allow the query (fail open)
            return True, ""

    async def _ai_classify_query(self, query: str) -> bool:
        """
        Use AI to classify if query is relevant to space biology
        Returns True if relevant, False otherwise
        """
        classification_prompt = f"""You are a classifier for a space biology research platform.

Determine if this query is relevant to space biology, microgravity research, astronaut health,
ISS experiments, or NASA-related biological/medical research.

Query: "{query}"

Respond with ONLY "YES" if relevant to space biology/research, or "NO" if completely unrelated.
Examples of relevant topics: microgravity effects, bone loss in space, muscle atrophy,
radiation biology, plant growth in space, cell biology, countermeasures, astronaut health.

Examples of irrelevant topics: making money, cooking recipes, sports, general news,
entertainment, fashion, generic business advice (unless space-industry related).

Answer:"""

        try:
            async with httpx.AsyncClient() as client:
                # Try Groq first (faster and free)
                response = await client.post(
                    f"{self.groq_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": classification_prompt}],
                        "max_tokens": 5,
                        "temperature": 0.1
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data['choices'][0]['message']['content'].strip().upper()
                    return 'YES' in answer
                else:
                    # Fallback: assume relevant if classification fails
                    return True

        except Exception as e:
            logger.error(f"AI classification error: {e}")
            # Fail open - allow query if we can't classify
            return True


# Singleton instance
context_guard = ContextGuard()
