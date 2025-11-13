from __future__ import annotations

import logging
import re
from typing import List, Optional

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

    def generate_sql(self, question: str, datasets: List[DatasetMetadata]) -> tuple[str | None, str | None]:
        """
        Generate SQL by showing LLM ALL available datasets and letting it choose the best one.
        The LLM will analyze the question, look at all schemas, and pick the right table.
        """
        if not datasets:
            return None, "No datasets available"
        
        # Build a combined schema showing ALL available tables
        all_schemas = self._build_multi_schema_prompt(datasets)
        
        system_prompt = (
            "You are an expert Kerala retail analytics assistant. "
            "Generate safe, efficient SQL queries for a SQLite database. "
            "The user question may be Malayalam, Manglish, or English. "
            "You have access to multiple tables - analyze the question and choose the most appropriate table."
        )
        user_prompt = self._build_multi_table_prompt(question, all_schemas)

        logger.info(
            "Generating SQL for question: '%s' | Available datasets: %s",
            question,
            [ds.dataset_type for ds in datasets],
        )

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
            logger.warning(
                "Failed to extract SQL from LLM output: %s | Question was: '%s'",
                llm_output,
                question,
            )
            return None, "Unable to parse SQL from model output"

        # Validate against ALL available tables
        validation_error = self._validate_sql_multi_table(sql_query, datasets)
        if validation_error:
            logger.warning("Generated SQL failed validation: %s", validation_error)
            return None, validation_error

        return sql_query, None

    # ------------------------------------------------------------------
    # Prompt helpers
    # ------------------------------------------------------------------
    def _build_multi_schema_prompt(self, datasets: List[DatasetMetadata]) -> str:
        """Build a combined schema description for ALL available datasets."""
        schema_sections = []
        
        for dataset in datasets:
            lines = [f"\n## Table: `{dataset.table_name}` (Dataset: {dataset.dataset_type})"]
            lines.append(f"Purpose: {self._get_table_purpose(dataset.dataset_type)}")
            lines.append(f"Rows: {dataset.row_count}")
            lines.append("Columns:")
            
            for column in dataset.columns:
                description = f" – {column.description}" if column.description else ""
                sample = ""
                if column.sample_values:
                    formatted_samples = ", ".join(str(v) for v in column.sample_values[:3])
                    sample = f" | examples: {formatted_samples}"
                lines.append(f"  - {column.name} ({column.dtype}){description}{sample}")
            
            schema_sections.append("\n".join(lines))
        
        return "\n".join(schema_sections)
    
    def _get_table_purpose(self, dataset_type: str) -> str:
        """Get a description of what each table is for."""
        purposes = {
            "sales": "Sales transactions, revenue, products sold, payment methods",
            "inventory": "Product stock levels, supplier information, reorder management",
            "staff": "Employee information, roles, shifts, work schedules",
            "transactions": "Financial transactions and payments",
            "customers": "Customer information and contact details",
        }
        return purposes.get(dataset_type.lower(), "Store data")
    
    def _build_multi_table_prompt(self, question: str, all_schemas: str) -> str:
        """Build prompt showing ALL available tables and asking LLM to choose."""
        rules = f"""You have access to MULTIPLE tables in the database. Analyze the question and choose the MOST APPROPRIATE table(s).

AVAILABLE TABLES:
{all_schemas}

RULES:
1. **Analyze the question carefully** - understand what data is needed
2. **Choose the table(s)** that best answer the question
3. **You can use JOINs** if the question requires data from multiple tables
   - Use common columns like `staff_id`, `sku`, `store_id` to JOIN tables
   - Example: To find staff with most sales, JOIN staff_raw with sales_raw ON staff_id
4. Use exact table names shown above
5. Return a single SELECT or WITH query. No DML/DDL, no comments, no semicolons
6. For counts use `COUNT(*)` or `COUNT(DISTINCT column)` as appropriate
7. For lists, include `ORDER BY` and apply `LIMIT` if appropriate (default {min(settings.MAX_ROWS, 100)})
8. For rankings/best/top, use `GROUP BY` with `ORDER BY` and `LIMIT`
9. Alias grouped results as `category` and numeric aggregations as `value` when appropriate
10. For date/time trends, alias columns as `date` and `value`
11. Ensure all column names exist exactly as shown in the schema
12. If the question cannot be answered with the available tables, respond with `-- NO_SQL`

USER QUESTION: {question}

Respond with ONLY the SQL query (no explanations, no markdown, just the SQL)."""
        
        return rules
    
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

    def _validate_sql_multi_table(self, sql_query: str, datasets: List[DatasetMetadata]) -> Optional[str]:
        """Validate SQL against ALL available tables. Allows JOINs."""
        upper = sql_query.upper()
        
        # Check for dangerous operations
        if any(keyword in upper for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "ATTACH", "DETACH", "PRAGMA"]):
            return "Only read-only SELECT queries are allowed"
        
        if sql_query.count(";") > 0:
            return "Multiple statements are not allowed"
        
        # Check if query references at least one valid table
        table_names = [ds.table_name for ds in datasets]
        table_found = False
        for table_name in table_names:
            # Check in FROM clause or JOIN clause
            pattern = r"\b(FROM|JOIN)\s+" + re.escape(table_name) + r"\b"
            if re.search(pattern, sql_query, flags=re.IGNORECASE):
                table_found = True
                break
        
        if not table_found:
            return f"Query must reference at least one of the available tables: {', '.join(table_names)}"
        
        # Verify all referenced tables are valid (prevent arbitrary table access)
        for match in re.finditer(r"\b(FROM|JOIN)\s+(\w+)", sql_query, flags=re.IGNORECASE):
            referenced_table = match.group(2)
            if referenced_table.lower() not in [tn.lower() for tn in table_names]:
                return f"Table '{referenced_table}' is not available. Use only: {', '.join(table_names)}"
        
        # Basic protection against SQLite PRAGMA or attaching other DBs
        if re.search(r"\b(PRAGMA|ATTACH|DETACH)\b", upper):
            return "Disallowed SQLite command detected"
        
        return None
    
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
