from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from sqlalchemy import text

from app.core.settings import settings
from app.services.dataset_manager import dataset_manager

logger = logging.getLogger(__name__)


class QueryExecutorService:
    """Execute validated SQL queries against store-scoped SQLite database."""

    def execute(self, store_id: str, sql_query: str) -> Dict[str, Any]:
        self._assert_read_only(sql_query)
        engine = dataset_manager.get_engine_for_store(store_id)
        rows: List[List[Any]] = []
        column_names: List[str] = []
        truncated = False

        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            if result.returns_rows:
                column_names = list(result.keys())
                for idx, row in enumerate(result):
                    if idx >= settings.MAX_ROWS:
                        truncated = True
                        break
                    rows.append([self._coerce_value(value) for value in row])
            else:
                raise ValueError("Query did not return any rows – ensure it is a SELECT statement")

        return {
            "columns": column_names,
            "rows": rows,
            "returned_rows": len(rows),
            "truncated": truncated,
            "has_more": len(rows) > settings.PREVIEW_ROWS,
        }

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def _assert_read_only(self, sql_query: str) -> None:
        upper = sql_query.upper()
        forbidden_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "PRAGMA",
            "ATTACH",
            "DETACH",
            "REPLACE",
            "CREATE",
            "VACUUM",
        ]
        if not re.match(r"\s*(SELECT|WITH)\b", upper):
            raise ValueError("Only SELECT queries are allowed")
        for keyword in forbidden_keywords:
            if f" {keyword} " in upper or upper.startswith(f"{keyword} "):
                raise ValueError(f"Keyword '{keyword}' is not allowed in queries")
        if ";" in sql_query.strip().strip(";"):
            raise ValueError("Multiple statements or semicolons are not allowed")

    def _coerce_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8")
            except Exception:
                return value.hex()
        return value


query_executor = QueryExecutorService()
__all__ = ["query_executor", "QueryExecutorService"]
