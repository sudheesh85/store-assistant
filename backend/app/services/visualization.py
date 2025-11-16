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

    def suggest(
        self, 
        question: str, 
        columns: List[str], 
        rows: List[List[Any]],
        intent: str = "data_query"
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest visualization based on intent and data structure.
        
        Args:
            question: User's question
            columns: Column names from query result
            rows: Data rows from query result
            intent: Intent classification result ("data_query", "insight", "reformat")
        """
        if not rows or not columns:
            return None

        num_cols = len(columns)
        num_rows = len(rows)

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
        
        # 3. Only "data_query" intent should get charts (insights/reformat don't need charts)
        if intent != "data_query":
            logger.info("No chart: Intent is '%s' (only data_query gets charts)", intent)
            return None
        
        # 4. Check if columns contain TEXT data (names, emails, IDs, etc.) - block charts
        text_column_indicators = ['name', 'email', 'phone', 'id', 'address', 'description', 'status', 'role']
        has_text_columns = any(
            any(indicator in col.lower() for indicator in text_column_indicators)
            for col in columns
        )
        if has_text_columns:
            logger.info("No chart: Data contains text columns (names, emails, etc.)")
            return None
        
        # 5. Special case: If data structure is "metric" and "value" (perfect for charts)
        # This is data-driven, not keyword-driven
        if num_cols == 2:
            col_names_lower = [col.lower() for col in columns]
            if ('metric' in col_names_lower or 'category' in col_names_lower) and \
               ('value' in col_names_lower or 'amount' in col_names_lower or 'count' in col_names_lower):
                logger.info("Detected metric/value structure - perfect for bar chart")
                # Proceed to chart generation (skip LLM, use fallback directly)
                return self._fallback_visualization(question, columns, rows)

        # Use LLM to decide chart type (if available)
        if self.client:
            return self._llm_based_visualization(question, columns, rows)
        else:
            # Fallback: simple rules based on data structure
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
        
        prompt = f"""Determine the best chart type for this data query result.

QUESTION: "{question}"
DATA: {num_cols} columns, {num_rows} rows
COLUMNS: {', '.join(columns)}
SAMPLE DATA: {rows[:3] if rows else 'No data'}

You already know this is a DATA QUERY (not insight/reformat), so focus on chart type selection.

Chart Type Rules:
- "bar" → Comparing multiple items/categories (top N, best/worst, performance metrics, metric/value pairs)
- "line" → Time series / trends over time (by date, by month, over time, trends)
- "metric" → Single number display (total count, single sum, one metric)
- "none" → Not suitable for visualization (detailed records, text data)

Examples:
- "top 5 products" → bar
- "sales by month" → line  
- "total revenue" → metric
- "performance metrics" (multiple rows) → bar
- "list all employees" → none

Respond with ONE WORD ONLY: bar / line / metric / none"""

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
                # Check if it's metric/value structure
                col_names_lower = [col.lower() for col in columns]
                if ('metric' in col_names_lower or 'category' in col_names_lower):
                    # Metric/value: values on X, metrics on Y
                    value_col_idx = 1 if 'value' in columns[1].lower() or 'amount' in columns[1].lower() or 'count' in columns[1].lower() else 0
                    metric_col_idx = 1 - value_col_idx
                    return {
                        "type": "bar_horizontal",
                        "x": columns[value_col_idx],
                        "y": columns[metric_col_idx],
                    }
                else:
                    # Regular bar chart
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
        
        # Metric/Value structure (perfect for bar chart)
        if num_cols == 2 and num_rows > 1:
            col_names_lower = [col.lower() for col in columns]
            if ('metric' in col_names_lower or 'category' in col_names_lower) and \
               ('value' in col_names_lower or 'amount' in col_names_lower or 'count' in col_names_lower):
                # Find which column is metric and which is value
                metric_col_idx = 0 if 'metric' in columns[0].lower() or 'category' in columns[0].lower() else 1
                value_col_idx = 1 - metric_col_idx
                
                logger.info("Fallback: Detected metric/value structure, generating bar chart")
                return {
                    "type": "bar_horizontal",
                    "x": columns[value_col_idx],  # Values on X axis
                    "y": columns[metric_col_idx],  # Metrics on Y axis
                }
        
        return None


default_visualizer = VisualizationService()
__all__ = ["default_visualizer", "VisualizationService"]
