from __future__ import annotations

import logging
import re
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]

from app.core.settings import settings
from app.services.dataset_manager import DatasetMetadata

logger = logging.getLogger(__name__)


class SQLGeneratorService:
    """Generate SQL from Malayalam/English natural language questions."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY missing – SQL generation will fail until provided.")
            self.client = None
        elif OpenAI is None:
            logger.warning("openai package is not installed – SQL generation disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_sql(self, question: str, dataset: DatasetMetadata) -> tuple[str | None, str | None]:
        schema_description = self._build_schema_prompt(dataset)
        system_prompt = (
            "You are an expert Kerala retail analytics assistant. "
            "Generate safe, efficient SQL queries for a SQLite database. "
            "The user question may be Malayalam, Manglish, or English."
        )
        user_prompt = self._build_user_prompt(question, dataset.table_name, schema_description)

        if not self.client:
            return None, "OPENAI_API_KEY is not configured"

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            logger.error("OpenAI chat completion failed: %s", exc, exc_info=True)
            return None, f"LLM error: {exc}"

        llm_output = response.choices[0].message.content if response.choices else ""
        sql_query = self._extract_sql(llm_output)
        if not sql_query:
            logger.warning("Failed to extract SQL from LLM output: %s", llm_output)
            return None, "Unable to parse SQL from model output"

        validation_error = self._validate_sql(sql_query, dataset.table_name)
        if validation_error:
            logger.warning("Generated SQL failed validation: %s", validation_error)
            return None, validation_error

        return sql_query, None

    # ------------------------------------------------------------------
    # Prompt helpers
    # ------------------------------------------------------------------
    def _build_schema_prompt(self, dataset: DatasetMetadata) -> str:
        lines = [f"Table `{dataset.table_name}` columns:"]
        for column in dataset.columns:
            description = f" – {column.description}" if column.description else ""
            sample = ""
            if column.sample_values:
                formatted_samples = ", ".join(str(v) for v in column.sample_values[:3])
                sample = f" | examples: {formatted_samples}"
            lines.append(f"- {column.name} ({column.dtype}){description}{sample}")
        lines.append(f"Total rows: {dataset.row_count}")
        return "\n".join(lines)

    def _build_user_prompt(self, question: str, table_name: str, schema_text: str) -> str:
        rules = f"""Follow these rules strictly:
1. Use only table `{table_name}`.
2. Return a single SELECT or WITH query. No DML/DDL, no comments, no semicolons.
3. For counts use `COUNT(*)` or `COUNT(DISTINCT column)` as appropriate.
4. For lists, include `ORDER BY` and apply `LIMIT` if the user didn't specify a size (default {min(settings.MAX_ROWS, 100)}).
5. Alias grouped results as `category` and numeric aggregations as `value` for charts when relevant.
6. For date/time trends, alias columns as `date` and `value`.
7. Ensure all column names exist exactly as shown in the schema.
8. If the question cannot be answered with SQL, respond with `-- NO_SQL`.
"""
        return (
            f"USER QUESTION:\n{question}\n\n"
            f"DATA SCHEMA:\n{schema_text}\n\n"
            f"{rules}\n"
            "Respond with only the SQL query (no explanations)."
        )

    # ------------------------------------------------------------------
    # Validation utilities
    # ------------------------------------------------------------------
    def _extract_sql(self, llm_output: str) -> Optional[str]:
        if not llm_output:
            return None
        fenced = re.search(r"```sql\s*([\s\S]*?)```", llm_output, flags=re.IGNORECASE)
        if fenced:
            candidate = fenced.group(1).strip()
        else:
            match = re.search(r"\b(SELECT|WITH)\b[\s\S]*", llm_output, flags=re.IGNORECASE)
            candidate = match.group(0).strip() if match else None
        if not candidate:
            return None
        # Remove trailing comments or markdown
        candidate = re.sub(r"```.*", "", candidate, flags=re.DOTALL)
        candidate = candidate.split(";", 1)[0]
        candidate = candidate.strip()
        return candidate if candidate else None

    def _validate_sql(self, sql_query: str, table_name: str) -> Optional[str]:
        upper = sql_query.upper()
        if any(keyword in upper for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "ATTACH", "DETACH", "PRAGMA"]):
            return "Only read-only SELECT queries are allowed"
        if sql_query.count(";") > 0:
            return "Multiple statements are not allowed"
        if not re.search(r"\bFROM\s+" + re.escape(table_name) + r"\b", sql_query, flags=re.IGNORECASE):
            return f"Query must reference table `{table_name}`"
        # Basic protection against SQLite PRAGMA or attaching other DBs
        if re.search(r"\b(PRAGMA|ATTACH|DETACH)\b", upper):
            return "Disallowed SQLite command detected"
        return None


sql_generator = SQLGeneratorService()
__all__ = ["sql_generator", "SQLGeneratorService"]
