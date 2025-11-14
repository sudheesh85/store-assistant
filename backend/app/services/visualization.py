from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]

from app.core.settings import settings

logger = logging.getLogger(__name__)


class VisualizationService:
    """Use LLM to intelligently decide if visualization is appropriate."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY missing – will use fallback visualization logic.")
            self.client = None
        elif OpenAI is None:
            logger.warning("openai package not installed – will use fallback visualization logic.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def suggest(self, question: str, columns: List[str], rows: List[List[Any]]) -> Optional[Dict[str, Any]]:
        """Use LLM to decide if chart is appropriate and what type."""
        if not rows or not columns:
            return None

        num_cols = len(columns)
        num_rows = len(rows)
        question_lower = question.lower()

        # ========================================
        # STRICT RULES: NO CHART for these cases
        # ========================================
        
        # 1. Too many columns = detailed data view
        if num_cols > 2:
            logger.info("No chart: Too many columns (%d > 2)", num_cols)
            return None
        
        # 2. No data
        if num_rows == 0:
            return None
        
        # ========================================
        # CHECK FOR CHART TRIGGERS FIRST (priority)
        # ========================================
        # - Aggregated metrics (top N, total, count, sum, average)
        # - Time series (trends over time)
        # - Comparisons (highest, lowest, best, worst)
        
        chart_trigger_keywords = [
            'top ', 'bottom ', 'highest', 'lowest', 'best', 'worst',
            'most', 'least', 'total', 'sum', 'average', 'count',
            'trend', 'over time', 'by month', 'by day', 'by year',
            'compare', 'comparison', 'growth', 'change'
        ]
        should_consider_chart = any(keyword in question_lower for keyword in chart_trigger_keywords)
        
        # If chart trigger found, skip list checks (trend/aggregation questions take priority)
        if should_consider_chart:
            # Only block if columns contain TEXT data (names, emails, IDs, etc.)
            text_column_indicators = ['name', 'email', 'phone', 'id', 'address', 'description', 'status', 'role']
            has_text_columns = any(
                any(indicator in col.lower() for indicator in text_column_indicators)
                for col in columns
            )
            if has_text_columns:
                logger.info("No chart: Data contains text columns (names, emails, etc.)")
                return None
            # Proceed to LLM/fallback for chart generation
        else:
            # No chart trigger found - apply strict blocking rules
            
            # 3. Questions asking about SPECIFIC people/entities (who is X, what is Y)
            specific_entity_patterns = [
                'who is', 'who are', 'what is', 'which is',
                'tell me about', 'show me about', 'details of',
                'information about', 'info about'
            ]
            if any(pattern in question_lower for pattern in specific_entity_patterns):
                logger.info("No chart: Question asks about specific entity")
                return None
            
            # 4. Questions asking for LISTS or ALL items
            list_keywords = [
                'list', 'show all', 'display all',
                'all staff', 'all products', 'all items', 'all sales',
            ]
            if any(keyword in question_lower for keyword in list_keywords):
                logger.info("No chart: Question asks for list/details")
                return None
            
            # 5. Check if columns contain TEXT data (names, emails, IDs, etc.)
            text_column_indicators = ['name', 'email', 'phone', 'id', 'address', 'description', 'status', 'role']
            has_text_columns = any(
                any(indicator in col.lower() for indicator in text_column_indicators)
                for col in columns
            )
            if has_text_columns:
                logger.info("No chart: Data contains text columns (names, emails, etc.)")
                return None
            
            # No clear chart trigger and no blocking rules matched
            logger.info("No chart: Question doesn't ask for aggregated/comparative data")
            return None

        # Use LLM to decide
        if self.client:
            return self._llm_based_visualization(question, columns, rows)
        else:
            # Fallback: simple rules
            return self._fallback_visualization(question, columns, rows)

    def _llm_based_visualization(
        self, question: str, columns: List[str], rows: List[List[Any]]
    ) -> Optional[Dict[str, Any]]:
        """Let LLM analyze question and decide if chart is needed."""
        
        num_cols = len(columns)
        num_rows = len(rows)
        
        # Build context about the data
        sample_data = rows[:3]  # First 3 rows
        data_summary = f"Columns: {', '.join(columns)}\nRows: {num_rows}\nSample: {sample_data}"
        
        prompt = f"""Does this question ask for AGGREGATED/COMPARATIVE data that NEEDS a chart?

QUESTION: "{question}"
DATA: {num_cols} columns, {num_rows} rows
COLUMNS: {', '.join(columns)}

⚠️ DEFAULT: "none" (NO CHART)

❌ MUST RETURN "none" IF:
- Asking about specific person/entity (who is X, what is Y)
- Wants to see details/records
- Text/categorical data (names, IDs, statuses)
- More than 2 columns

✅ ONLY return chart type IF:
- "top N" / "highest" / "lowest" / "best" / "worst" → "bar"
- "trend" / "over time" / "by month" → "line"
- "total" / "count" / "sum" (SINGLE NUMBER) → "metric"

Respond with ONE WORD ONLY: none / bar / line / metric"""

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                max_tokens=10,
                messages=[
                    {"role": "system", "content": "You are a data visualization expert."},
                    {"role": "user", "content": prompt},
                ],
            )
            
            chart_type = response.choices[0].message.content.strip().lower() if response.choices else "none"
            
            logger.info(
                "LLM visualization decision for '%s': %s (cols=%d, rows=%d)",
                question,
                chart_type,
                num_cols,
                num_rows,
            )
            
            if chart_type == "none":
                return None
            
            # Build appropriate chart config
            if chart_type == "metric" and num_cols == 1 and num_rows == 1:
                return {
                    "type": "metric",
                    "value_column": columns[0],
                    "title": question,
                }
            elif chart_type == "bar" and num_cols == 2:
                return {
                    "type": "bar_horizontal",
                    "x": columns[1],
                    "y": columns[0],
                }
            elif chart_type == "line" and num_cols == 2:
                return {
                    "type": "line",
                    "x": columns[0],
                    "y": columns[1],
                }
            elif chart_type == "pie" and num_cols == 2:
                return {
                    "type": "pie",
                    "labels": columns[0],
                    "values": columns[1],
                }
            
            return None
            
        except Exception as exc:
            logger.error("LLM visualization decision failed: %s", exc)
            return self._fallback_visualization(question, columns, rows)

    def _fallback_visualization(
        self, question: str, columns: List[str], rows: List[List[Any]]
    ) -> Optional[Dict[str, Any]]:
        """Simple fallback when LLM unavailable."""
        num_cols = len(columns)
        num_rows = len(rows)
        
        # Only single numeric metric
        if num_cols == 1 and num_rows == 1:
            try:
                float(rows[0][0])
                return {
                    "type": "metric",
                    "value_column": columns[0],
                    "title": question,
                }
            except (ValueError, TypeError):
                pass
        
        return None


default_visualizer = VisualizationService()
__all__ = ["default_visualizer", "VisualizationService"]
