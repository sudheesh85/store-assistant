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
from app.services.query_executor import query_executor

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

        # If context_data already provided (from previous query), extract entity and get detailed data
        if context_data and context_data.get("rows"):
            # Extract name from previous result
            enriched_data = self._enrich_context_with_performance(context_data, store_id, datasets)
            if enriched_data:
                context_data = enriched_data
        else:
            # Fetch relevant data if question mentions specific entities
            fetched_data = self._fetch_relevant_data(question, store_id, datasets)
            if fetched_data:
                context_data = fetched_data

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
        person_name = None
        
        # Extract person's name if we have specific data
        if has_recent_data:
            cols = context_data.get('columns', [])
            rows = context_data.get('rows', [])
            if rows and cols:
                data_dict = dict(zip(cols, rows[0]))
                person_name = data_dict.get("name") or data_dict.get("staff_name")
        
        if has_recent_data:
            name_instruction = ""
            if person_name:
                name_instruction = f"\n\n🎯 CRITICAL: The data above is for {person_name.upper()}. Give advice SPECIFICALLY for {person_name} based on THEIR actual numbers (mention the numbers!), NOT generic advice.\n"
            
            prompt = f"""You are a helpful virtual assistant for a Kerala retail store manager. They just looked at performance data and now want improvement advice.

THEIR QUESTION: {question}

{data_context}{name_instruction}

RESPOND AS A HELPFUL COLLEAGUE:
- Be conversational and friendly (like chatting with a coworker)
- Keep it SHORT (3-4 sentences max)
- Give SPECIFIC, ACTIONABLE advice for {"" + person_name + "" if person_name else "this person"} based on THE ACTUAL NUMBERS shown in the data above
- Use simple language, NO technical jargon
- MENTION the specific performance metrics (sales count, revenue, etc.) from the data
- Be encouraging but practical
- {"Use '" + person_name + "' or 'he/she'" if person_name else "Reference the person"}

Example: "{person_name if person_name else 'He'} has 45 sales worth ₹12,500. To improve, focus on upselling higher-value items and follow up with regular customers."
NOT: "To improve performance, implement structured training programs and analyze sales metrics."

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

    def _enrich_context_with_performance(
        self,
        context_data: Dict[str, Any],
        store_id: str,
        datasets: List[DatasetMetadata],
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich previous query result with detailed performance data.
        Extracts entity name from context_data and fetches their performance metrics.
        """
        try:
            cols = context_data.get("columns", [])
            rows = context_data.get("rows", [])
            
            if not rows or not cols:
                return None
            
            # Extract person's name from the result
            first_row = rows[0]
            data_dict = dict(zip(cols, first_row))
            person_name = data_dict.get("name") or data_dict.get("staff_name")
            
            if not person_name:
                # No name found in previous result
                return None
            
            logger.info("Enriching context for entity: %s", person_name)
            
            # Get staff and sales datasets
            staff_dataset = next((ds for ds in datasets if ds.dataset_type == "staff"), None)
            sales_dataset = next((ds for ds in datasets if ds.dataset_type == "sales"), None)
            
            if not staff_dataset or not sales_dataset:
                return None
            
            # Get staff_id for this person
            staff_sql = f"SELECT * FROM {staff_dataset.table_name} WHERE name = :person_name LIMIT 1"
            staff_result = query_executor.execute(store_id, staff_sql, {"person_name": person_name})
            
            if not staff_result or not staff_result["rows"]:
                return None
            
            staff_row = dict(zip(staff_result["columns"], staff_result["rows"][0]))
            staff_id = staff_row.get("staff_id")
            
            if not staff_id:
                return None
            
            # Get detailed sales performance
            sales_sql = f"""
            SELECT 
                COUNT(*) as total_sales,
                SUM(total_price) as total_revenue,
                AVG(total_price) as avg_transaction,
                MIN(sale_date) as first_sale_date,
                MAX(sale_date) as last_sale_date
            FROM {sales_dataset.table_name}
            WHERE staff_id = :staff_id
            """
            sales_result = query_executor.execute(store_id, sales_sql, {"staff_id": staff_id})
            
            if not sales_result or not sales_result["rows"]:
                return None
            
            # Combine staff info with sales performance
            combined_data = {
                "columns": staff_result["columns"] + sales_result["columns"],
                "rows": [staff_result["rows"][0] + sales_result["rows"][0]],
                "context": f"Detailed performance data for {person_name}"
            }
            
            logger.info("Successfully enriched data for %s", person_name)
            return combined_data
            
        except Exception as exc:
            logger.warning("Failed to enrich context with performance data: %s", exc)
            return None
    
    def _fetch_relevant_data(
        self,
        question: str,
        store_id: str,
        datasets: List[DatasetMetadata],
    ) -> Optional[Dict[str, Any]]:
        """Fetch relevant data if question mentions specific entities (people, products, etc.)."""
        try:
            # Check if question mentions a name (likely staff)
            # Look for capitalized words that might be names
            question_words = question.split()
            potential_names = [word.strip(".,!?:|-") for word in question_words if word and len(word) > 0 and word[0].isupper()]
            
            # Filter out common words that aren't names
            common_words = {'Previous', 'Context', 'Current', 'Question', 'The', 'How', 'Can', 'We', 'I', 'You'}
            potential_names = [name for name in potential_names if name not in common_words and len(name) > 2]
            
            if not potential_names:
                return None
            
            # Check if we have staff data
            staff_dataset = next((ds for ds in datasets if ds.dataset_type == "staff"), None)
            sales_dataset = next((ds for ds in datasets if ds.dataset_type == "sales"), None)
            
            if not staff_dataset:
                return None
            
            # Try to find the mentioned person in staff data
            for name in potential_names:
                if len(name) < 3:  # Skip short words
                    continue
                
                # Query staff data for this person
                # Use parameterized query for safety
                sql = f"SELECT * FROM {staff_dataset.table_name} WHERE name LIKE :name_pattern LIMIT 1"
                try:
                    staff_result = query_executor.execute(store_id, sql, {"name_pattern": f"%{name}%"})
                    if staff_result and staff_result["rows"]:
                        # Found the person! Now get their sales performance
                        staff_row = dict(zip(staff_result["columns"], staff_result["rows"][0]))
                        staff_id = staff_row.get("staff_id")
                        
                        if staff_id and sales_dataset:
                            # Get sales performance for this staff member
                            sales_sql = f"""
                            SELECT 
                                COUNT(*) as total_sales,
                                SUM(total_price) as total_revenue,
                                AVG(total_price) as avg_transaction
                            FROM {sales_dataset.table_name}
                            WHERE staff_id = :staff_id
                            """
                            sales_result = query_executor.execute(store_id, sales_sql, {"staff_id": staff_id})
                            
                            # Combine staff info with sales performance
                            combined_data = {
                                "columns": staff_result["columns"] + sales_result["columns"],
                                "rows": [staff_result["rows"][0] + sales_result["rows"][0]],
                                "context": f"Performance data for {name}"
                            }
                            
                            logger.info("Fetched data for entity: %s", name)
                            return combined_data
                except Exception as e:
                    logger.debug("Failed to fetch data for %s: %s", name, e)
                    continue
            
            return None
        except Exception as exc:
            logger.warning("Error fetching relevant data: %s", exc)
            return None


insights_generator = InsightsGenerator()

__all__ = ["insights_generator", "InsightsGenerator"]

