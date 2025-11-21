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

    def generate_sql(
        self, 
        question: str, 
        datasets: List[DatasetMetadata],
        conversation_context: Optional[List[str]] = None
    ) -> tuple[str | None, str | None]:
        """
        Generate SQL by showing LLM ALL available datasets and letting it choose the best one.
        Uses conversation context to understand follow-up questions.
        """
        if not datasets:
            return None, "No datasets available"
        
        # Build a combined schema showing ALL available tables
        all_schemas = self._build_multi_schema_prompt(datasets)
        
        system_prompt = (
            "You are an expert SQL query generator for retail analytics. "
            "Generate ONLY valid SQLite SELECT queries - no explanations, no comments, no markdown. "
            "CRITICAL: Your response must start with SELECT or WITH. "
            "The user question may be in Malayalam, Manglish, or English. "
            "You have access to multiple tables - analyze the question and choose the most appropriate table(s). "
            "Use conversation context to understand follow-up questions with pronouns (they/them/those). "
            "If a follow-up asks 'who are they' after 'how many employees', list the employees."
        )
        user_prompt = self._build_multi_table_prompt(question, all_schemas, conversation_context)

        logger.info(
            "Generating SQL for question: '%s' | Available datasets: %s",
            question,
            [ds.dataset_type for ds in datasets],
        )

        if not self.client:
            return None, "OpenAI API key is not configured. Please add OPENAI_API_KEY to your .env file."

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
            logger.error(
                "Failed to extract SQL from LLM output: %s | Question was: '%s'",
                llm_output,
                question,
            )
            # Return the actual LLM output for debugging
            error_msg = f"Unable to generate SQL query. LLM response: {llm_output[:200]}"
            return None, error_msg
        
        logger.info("Generated SQL: %s", sql_query)

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
    
    def _build_multi_table_prompt(
        self, 
        question: str, 
        all_schemas: str,
        conversation_context: Optional[List[str]] = None
    ) -> str:
        """Build prompt showing ALL available tables and asking LLM to choose."""
        
        context_section = ""
        if conversation_context and len(conversation_context) > 0:
            context_section = f"""
⚠️ CONVERSATION CONTEXT (Previous questions in this conversation):
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(conversation_context))}

🔑 IMPORTANT: Use this context to understand follow-up questions with pronouns:
- If previous question asked "how many employees" and current is "who are they", 
  → Generate a query to list all employees (SELECT * FROM staff_raw)
- If previous was "total sales" and current is "show them", 
  → Generate query to list sales records
- If previous was "who is the best salesperson" and current is "who is the weakest",
  → Generate similar query but ORDER BY ASC instead of DESC or MIN instead of MAX
- Pronouns like "they/them/those/these" refer to entities from the previous question

"""
        
        rules = f"""You have access to MULTIPLE tables in the database. Analyze the question and choose the MOST APPROPRIATE table(s).

AVAILABLE TABLES:
{all_schemas}
{context_section}
RULES:
1. **Analyze the question carefully** - understand what data is needed
2. **Use conversation context** to understand pronouns and follow-up questions
3. **Choose the table(s)** that best answer the question
4. **You can use JOINs** if the question requires data from multiple tables
   - Use common columns like `staff_id`, `sku`, `store_id` to JOIN tables
   - Example: To find staff with most sales, JOIN staff_raw with sales_raw ON staff_id
5. Use exact table names shown above
6. Return a single SELECT or WITH query. No DML/DDL, no comments, no semicolons
7. For counts use `COUNT(*)` or `COUNT(DISTINCT column)` as appropriate
8. For lists, include `ORDER BY` and apply `LIMIT` if appropriate (default {min(settings.MAX_ROWS, 100)})
9. For rankings/best/top, use `GROUP BY` with `ORDER BY` and `LIMIT`
10. Alias grouped results as `category` and numeric aggregations as `value` when appropriate
11. For date/time trends, alias columns as `date` and `value`
12. Ensure all column names exist exactly as shown in the schema
13. **Infer reasonable logic for qualitative terms**:
    - "Low stock" / "Running out" → ORDER BY stock/quantity ASC LIMIT 10
    - "Best selling" → ORDER BY total_sales DESC LIMIT 10
    - "Recent" → ORDER BY date_column DESC LIMIT 10
14. **Malayalam/Manglish Support**:
    - "സ്റ്റോക്ക് കുറവുള്ള items?" (Items with low stock?) → SELECT * FROM inventory_raw ORDER BY stock_on_hand ASC LIMIT 10
    - "കൂടുതൽ വിറ്റ സാധനങ്ങൾ" (Most sold items) → Aggregated sales query
15. If the question cannot be answered with the available tables, respond with `-- NO_SQL`

USER QUESTION: {question}

⚠️ CRITICAL: Your response must contain ONLY the SQL query. 
- NO explanations before or after
- NO markdown formatting
- NO comments
- Just the raw SQL SELECT statement
- Start your response directly with SELECT or WITH

Example response format:
SELECT * FROM sales_raw WHERE date = '2024-01-01'"""
        
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
        
        # Log the raw output for debugging
        logger.info("Raw LLM output for SQL extraction: %s", llm_output[:500])
        
        # Try multiple extraction strategies
        
        # 1. Try to extract from SQL code fence
        fenced = re.search(r"```sql\s*([\s\S]*?)```", llm_output, flags=re.IGNORECASE)
        if fenced:
            candidate = fenced.group(1).strip()
        # 2. Try generic code fence (might have no language tag)
        elif re.search(r"```\s*(SELECT|WITH)\b", llm_output, flags=re.IGNORECASE):
            generic_fence = re.search(r"```\s*([\s\S]*?)```", llm_output, flags=re.IGNORECASE)
            if generic_fence:
                candidate = generic_fence.group(1).strip()
            else:
                candidate = None
        # 3. Try to find SELECT/WITH statement
        else:
            # Look for SELECT or WITH followed by everything until we hit common endings
            match = re.search(
                r"\b(SELECT|WITH)\b[\s\S]*?(?=(?:\n\n|$|```|Answer:|Explanation:|Note:))",
                llm_output,
                flags=re.IGNORECASE
            )
            candidate = match.group(0).strip() if match else None
        
        if not candidate:
            # 4. Last resort: check if the entire output looks like SQL
            stripped = llm_output.strip()
            if stripped.upper().startswith(("SELECT", "WITH")):
                candidate = stripped
            else:
                logger.warning("Could not extract SQL from output: %s", llm_output[:200])
                return None
        
        # Clean up the candidate
        # Remove trailing markdown or comments
        candidate = re.sub(r"```.*", "", candidate, flags=re.DOTALL)
        # Remove semicolons
        candidate = candidate.split(";", 1)[0]
        # Remove inline SQL comments (-- comments)
        candidate = re.sub(r"--[^\n]*", "", candidate)
        # Remove block comments (/* ... */)
        candidate = re.sub(r"/\*[\s\S]*?\*/", "", candidate)
        candidate = candidate.strip()
        
        # Final validation
        if candidate and len(candidate) > 10:
            logger.info("Extracted SQL: %s", candidate)
            return candidate
        
        logger.warning("SQL extraction failed - candidate too short or empty")
        return None

    def _validate_sql_multi_table(self, sql_query: str, datasets: List[DatasetMetadata]) -> Optional[str]:
        """Validate SQL against ALL available tables. Allows JOINs."""
        upper = sql_query.upper()
        
        # Check for dangerous operations
        # Check for dangerous operations using word boundaries
        forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "ATTACH", "DETACH", "PRAGMA"]
        for keyword in forbidden_keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", upper):
                return f"Only read-only SELECT queries are allowed (detected forbidden keyword: {keyword})"
        
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
