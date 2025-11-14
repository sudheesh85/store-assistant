from __future__ import annotations

import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]

from app.core.settings import settings

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classify user query intent using LLM."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY missing – intent classification will default to 'data_query'.")
            self.client = None
        elif OpenAI is None:
            logger.warning("openai package not installed – intent classification will default to 'data_query'.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def classify(self, question: str, has_context: bool = False) -> str:
        """
        Classify question intent.
        
        Returns:
            "data_query" - needs SQL execution (e.g., "show sales", "top products")
            "insight" - needs analysis/recommendations (e.g., "how to improve", "what should I do")
            "reformat" - wants to reformat previous answer (e.g., "in malayalam", "translate", "explain")
        """
        if not self.client:
            return "data_query"

        context_note = " (User has conversation context - might be follow-up question)" if has_context else ""

        prompt = f"""Classify this question intent:{context_note}

QUESTION: {question}

Is this a:
A) DATA QUERY - user wants to see/fetch NEW data (show, list, get, how many, what are, top, total, who is, which)
B) INSIGHT/ADVICE - user wants recommendations/analysis (how to improve, what should I do, suggestions, advice, why, strategy)
C) REFORMAT - user wants previous answer reformatted/translated (in malayalam, translate, explain, tell me in, give me in, can you give)

Respond with ONLY ONE WORD:
- "data_query" (if asking for NEW data or specific information)
- "insight" (if asking for recommendations/analysis/strategy)
- "reformat" (if asking to translate/reformat previous answer)"""

        try:
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
            
            logger.info("Classified intent for '%s': %s", question[:50], intent)
            
            # Validate intent
            return intent if intent in ["data_query", "insight", "reformat"] else "data_query"

        except Exception as exc:
            logger.error("Intent classification failed: %s", exc)
            return "data_query"


intent_classifier = IntentClassifier()
__all__ = ["intent_classifier", "IntentClassifier"]




