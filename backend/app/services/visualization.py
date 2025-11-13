from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VisualizationService:
    """Infer reasonable chart defaults based on question and result shape."""

    def suggest(self, question: str, columns: List[str], rows: List[List[Any]]) -> Optional[Dict[str, Any]]:
        if not rows or not columns:
            return None

        q = question.lower()
        num_cols = len(columns)
        num_rows = len(rows)

        # Single value metric
        if num_cols == 1 and num_rows == 1:
            return {
                "type": "metric",
                "value_column": columns[0],
                "title": question,
            }

        # Grouped counts (category/value)
        if num_cols == 2 and num_rows > 1:
            cat_col, val_col = columns[0], columns[1]
            if any(keyword in q for keyword in ["distribution", "breakdown", "share", "status"]):
                return {
                    "type": "pie",
                    "labels": cat_col,
                    "values": val_col,
                }
            if any(keyword in q for keyword in ["top", "best", "highest", "lowest"]):
                return {
                    "type": "bar_horizontal",
                    "x": val_col,
                    "y": cat_col,
                }
            return {
                "type": "bar",
                "x": cat_col,
                "y": val_col,
            }

        # Time series heuristics
        if num_cols >= 2:
            first_sample = str(rows[0][0]).lower()
            looks_like_date = any(token in first_sample for token in ["202", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "-", "/"])
            if looks_like_date or any(keyword in q for keyword in ["trend", "over time", "daily", "monthly", "weekly", "year"]):
                return {
                    "type": "line",
                    "x": columns[0],
                    "y": columns[1],
                }

        # Scatter chart for two numeric columns
        if num_cols == 2 and num_rows > 1:
            try:
                float(rows[0][0])
                float(rows[0][1])
                return {
                    "type": "scatter",
                    "x": columns[0],
                    "y": columns[1],
                }
            except Exception:
                pass

        return None


default_visualizer = VisualizationService()
__all__ = ["default_visualizer", "VisualizationService"]
