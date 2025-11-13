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

        # Basic checks - never chart these
        if num_cols > 3 or num_rows == 0:
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
        
        prompt = f"""Analyze this question and data to decide if a chart/visualization is appropriate.

QUESTION: {question}

DATA:
{data_summary}

RULES:
1. If user asks for a LIST (list, show, display, pls, who, details, all) → NO CHART (return "none")
2. If data has many text columns (names, emails, etc.) → NO CHART
3. If user asks for comparison/ranking (top, best, highest) → BAR CHART
4. If user asks for single total/count (total, sum, count) → METRIC
5. If user asks for trend (over time, daily, monthly) → LINE CHART
6. If data has dates in first column + numbers → LINE CHART
7. Default for unclear cases → NO CHART

Respond with ONLY ONE WORD:
- "none" (no chart, show table)
- "bar" (bar chart for comparisons)
- "line" (line chart for trends)
- "metric" (single number display)
- "pie" (distribution/percentage)"""

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
