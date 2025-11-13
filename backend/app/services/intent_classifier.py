from __future__ import annotations

import logging
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]

from app.core.settings import settings

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classify user question intent: data query vs insight/recommendation request."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY missing – intent classification will use fallback.")
            self.client = None
        elif OpenAI is None:
            logger.warning("openai package not installed – intent classification disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def classify(self, question: str, has_context: bool = False) -> str:
        """
        Classify question intent.
        
        Returns:
            "data_query" - needs SQL execution (e.g., "show sales", "top products")
            "insight" - needs analysis/recommendations (e.g., "how to improve", "what should I do")
        """
        if not self.client:
            return self._fallback_classify(question)

        try:
            context_note = " User has previous query results visible." if has_context else ""
            
            prompt = f"""Classify this question intent:{context_note}

QUESTION: {question}

Is this a:
A) DATA QUERY - user wants to see/fetch data (show, list, get, how many, what are, top, total)
B) INSIGHT/ADVICE - user wants recommendations/analysis (how to improve, what should I do, suggestions, advice, why)

Respond with ONLY ONE WORD:
- "data_query" (if asking for data)
- "insight" (if asking for recommendations/analysis)"""

            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                max_tokens=10,
                messages=[
                    {"role": "system", "content": "You are an intent classification expert."},
                    {"role": "user", "content": prompt},
                ],
            )

            intent = response.choices[0].message.content.strip().lower() if response.choices else "data_query"
            
            logger.info("Intent classification for '%s': %s", question, intent)
            
            return intent if intent in ["data_query", "insight"] else "data_query"

        except Exception as exc:
            logger.error("Intent classification failed: %s", exc)
            return self._fallback_classify(question)

    def _fallback_classify(self, question: str) -> str:
        """Simple keyword-based fallback."""
        q = question.lower()
        
        insight_keywords = [
            "how to", "how can", "what should", "improve", "increase", "decrease",
            "suggest", "recommend", "advice", "why", "strategy", "better", "optimize"
        ]
        
        if any(keyword in q for keyword in insight_keywords):
            return "insight"
        
        return "data_query"


intent_classifier = IntentClassifier()

__all__ = ["intent_classifier", "IntentClassifier"]

