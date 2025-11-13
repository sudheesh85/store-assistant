from __future__ import annotations

import json
import logging
from typing import Any, List

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]

from app.core.settings import settings
from app.utils.language import should_respond_in_malayalam

logger = logging.getLogger(__name__)


class ExplanationService:
    """Generate Malayalam / English explanations for SQL query results."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY missing – explanations will fail until provided.")
            self.client = None
        elif OpenAI is None:
            logger.warning("openai package is not installed – explanation generation disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate(
        self,
        question: str,
        columns: List[str],
        rows: List[List[Any]],
    ) -> str:
        if not rows:
            return "ഡാറ്റ ലഭ്യമല്ല. മറ്റൊരു ചോദ്യം ശ്രമിക്കൂ." if should_respond_in_malayalam(question) else "No data found for this question. Try adjusting the filters."

        if not self.client:
            return "OPENAI_API_KEY ക്രമീകരിച്ചിട്ടില്ല." if should_respond_in_malayalam(question) else "OPENAI_API_KEY is not configured."

        payload = [
            {col: self._to_serializable(val) for col, val in zip(columns, row)}
            for row in rows[:10]
        ]
        language = "Malayalam" if should_respond_in_malayalam(question) else "English"
        system_prompt = (
            "You are a friendly analytics assistant for Kerala retail store owners. "
            "Explain SQL query results in simple {}.".format(language)
        )
        user_prompt = (
            f"Question: {question}\n"
            f"Answer in {language}. Use a warm, helpful tone."
            "\nSummarise the key insight from these results in 2-3 sentences."
            "\nIf appropriate, mention trends or comparisons."
            "\nAvoid technical jargon."
            f"\nResults JSON (first {len(payload)} rows):\n{json.dumps(payload, ensure_ascii=False)}"
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            logger.error("Explanation generation failed: %s", exc, exc_info=True)
            return "കുറിപ്പ് സൃഷ്ടിക്കാൻ കഴിഞ്ഞില്ല." if language == "Malayalam" else "Unable to generate explanation."

        return response.choices[0].message.content.strip() if response.choices else ""

    def _to_serializable(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (int, float, str, bool)):
            return value
        try:
            return str(value)
        except Exception:
            return repr(value)


default_explanation_service = ExplanationService()
__all__ = ["default_explanation_service", "ExplanationService"]
