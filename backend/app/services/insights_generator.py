from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]

from app.core.settings import settings
from app.services.dataset_manager import DatasetMetadata, dataset_manager

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """Generate insights, recommendations, and advice based on available data."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY missing – insights generation disabled.")
            self.client = None
        elif OpenAI is None:
            logger.warning("openai package not installed – insights generation disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate(
        self,
        question: str,
        store_id: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate insights/recommendations for the question.
        
        Args:
            question: User's question asking for advice/insights
            store_id: Store ID to fetch data context
            context_data: Previous query results if available
        """
        if not self.client:
            return "Insights generation is not available. Please configure OPENAI_API_KEY."

        # Get available datasets for context
        datasets = dataset_manager.list_datasets(store_id)
        if not datasets:
            return "No data available to provide insights. Please upload data first."

        # Build context about available data
        data_context = self._build_data_context(datasets, context_data)

        # Generate insights using LLM
        try:
            prompt = self._build_insights_prompt(question, data_context, context_data)
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly virtual assistant helping a Kerala store manager. "
                                   "Talk like a helpful coworker, not a consultant. "
                                   "Keep responses short, simple, and actionable."
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            insight = response.choices[0].message.content.strip() if response.choices else ""
            
            logger.info("Generated insights for question: '%s'", question)
            
            return insight or "I need more specific data to provide meaningful recommendations."

        except Exception as exc:
            logger.error("Insights generation failed: %s", exc, exc_info=True)
            return "Unable to generate insights at the moment. Please try rephrasing your question."

    def _build_data_context(
        self,
        datasets: List[DatasetMetadata],
        context_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build context about available data."""
        context_lines = ["AVAILABLE DATA:"]
        
        for ds in datasets:
            context_lines.append(f"\n{ds.dataset_type.upper()} data ({ds.row_count} rows):")
            context_lines.append(f"  Columns: {', '.join([col.name for col in ds.columns[:10]])}")
        
        if context_data and context_data.get("columns") and context_data.get("rows"):
            context_lines.append("\n\nRECENT QUERY RESULTS:")
            context_lines.append(f"  Columns: {', '.join(context_data['columns'])}")
            context_lines.append(f"  Sample rows: {json.dumps(context_data['rows'][:5], ensure_ascii=False)}")
        
        return "\n".join(context_lines)

    def _build_insights_prompt(
        self,
        question: str,
        data_context: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build prompt for insights generation."""
        
        has_recent_data = context_data and context_data.get("rows")
        
        if has_recent_data:
            prompt = f"""You are a helpful virtual assistant for a Kerala retail store manager. They just looked at some data and now want advice.

THEIR QUESTION: {question}

{data_context}

RESPOND AS A HELPFUL COLLEAGUE:
- Be conversational and friendly (like chatting with a coworker)
- Keep it SHORT (3-4 sentences max)
- Give SPECIFIC, ACTIONABLE advice they can do TODAY
- Use simple language, NO technical jargon
- Reference the actual data they just saw
- Be encouraging and practical

Example tone: "Based on what we're seeing, here's what I'd suggest..."
NOT: "To improve sales metrics, implement the following structured approach..."

Respond naturally in Malayalam or English (match their question language)."""
        else:
            prompt = f"""You are a helpful virtual assistant for a Kerala retail store manager. They're asking for advice.

THEIR QUESTION: {question}

{data_context}

RESPOND AS A HELPFUL COLLEAGUE:
- Be conversational and friendly
- Keep it SHORT (3-4 quick tips)
- Give PRACTICAL advice they can act on immediately
- Use simple language
- Suggest checking specific data first: "Let me first check..." or "Let's look at..."
- Be encouraging

Example: "Good question! Let's check a few things. First, let's see how [product] has been selling this month. Then..."
NOT: "To analyze this, you should run the following queries: 1. Sales trends 2. Inventory levels..."

Respond naturally in Malayalam or English (match their question language)."""

        return prompt


insights_generator = InsightsGenerator()

__all__ = ["insights_generator", "InsightsGenerator"]

