from __future__ import annotations

import logging
from typing import List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]

from app.core.settings import settings
from app.services.dataset_manager import DatasetMetadata, dataset_manager

logger = logging.getLogger(__name__)


class DatasetRouterService:
    """Intelligently routes questions to the appropriate dataset/table."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY missing – dataset routing will use fallback logic.")
            self.client = None
        elif OpenAI is None:
            logger.warning("openai package is not installed – dataset routing will use fallback logic.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def route_question(
        self,
        question: str,
        store_id: str,
    ) -> Optional[DatasetMetadata]:
        """
        Analyze the question and route it to the most appropriate dataset.
        Returns the best-matching dataset metadata.
        """
        datasets = dataset_manager.list_datasets(store_id)
        
        if not datasets:
            logger.warning("No datasets available for store %s", store_id)
            return None
        
        if len(datasets) == 1:
            # Only one dataset available, use it
            logger.info("Only one dataset available, using: %s", datasets[0].dataset_type)
            return datasets[0]
        
        # Multiple datasets - need to be intelligent about routing
        if self.client:
            return self._llm_based_routing(question, datasets)
        else:
            return self._keyword_based_routing(question, datasets)

    def _llm_based_routing(
        self,
        question: str,
        datasets: List[DatasetMetadata],
    ) -> Optional[DatasetMetadata]:
        """Use LLM to intelligently route the question to the right dataset."""
        
        # Build dataset descriptions
        dataset_descriptions = []
        for ds in datasets:
            columns = ", ".join([col.name for col in ds.columns])
            desc = (
                f"- {ds.dataset_type}: table '{ds.table_name}' with {ds.row_count} rows\n"
                f"  Columns: {columns}\n"
                f"  Description: {self._get_dataset_description(ds.dataset_type)}"
            )
            dataset_descriptions.append(desc)
        
        datasets_text = "\n".join(dataset_descriptions)
        
        prompt = f"""You are a data routing assistant. Given a user's question and available datasets, determine which dataset is most appropriate.

AVAILABLE DATASETS:
{datasets_text}

USER QUESTION: {question}

Analyze the question and respond with ONLY the dataset type name (e.g., 'sales', 'inventory', 'staff') that best matches this question.
If the question could apply to multiple datasets, choose the most relevant one.
Respond with just the dataset type name, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": "You are a data routing expert for retail stores."},
                    {"role": "user", "content": prompt},
                ],
            )
            
            llm_choice = response.choices[0].message.content.strip().lower() if response.choices else ""
            
            logger.info(
                "LLM routing for question '%s': chose dataset '%s'",
                question,
                llm_choice,
            )
            
            # Find matching dataset
            for ds in datasets:
                if ds.dataset_type.lower() == llm_choice:
                    return ds
            
            # If no exact match, try partial match
            for ds in datasets:
                if llm_choice in ds.dataset_type.lower() or ds.dataset_type.lower() in llm_choice:
                    return ds
            
            logger.warning("LLM returned unrecognized dataset type: %s", llm_choice)
            
        except Exception as exc:
            logger.error("LLM-based routing failed: %s", exc, exc_info=True)
        
        # Fallback to keyword-based routing
        return self._keyword_based_routing(question, datasets)

    def _keyword_based_routing(
        self,
        question: str,
        datasets: List[DatasetMetadata],
    ) -> Optional[DatasetMetadata]:
        """Fallback: Use keyword matching to route the question."""
        
        question_lower = question.lower()
        
        # Define keywords for each common dataset type
        routing_rules = {
            "inventory": [
                "inventory", "stock", "product", "item", "reorder", "supplier",
                "qty", "quantity", "in stock", "available", "warehouse", "sku",
                "സ്റ്റോക്ക്", "ഉൽപ്പന്നം", "സാധനം"
            ],
            "sales": [
                "sale", "sold", "revenue", "income", "transaction", "purchase",
                "payment", "customer", "order", "total", "earnings", "profit",
                "വിൽപ്പന", "വരുമാനം", "ഇടപാട്"
            ],
            "staff": [
                "staff", "employee", "worker", "team", "person", "manager",
                "cashier", "role", "shift", "work", "hired",
                "ജീവനക്കാർ", "ജോലിക്കാർ", "ടീം"
            ],
        }
        
        # Score each dataset based on keyword matches
        scores = {}
        for ds in datasets:
            score = 0
            dataset_type_lower = ds.dataset_type.lower()
            
            # Check if dataset type matches common patterns
            if dataset_type_lower in routing_rules:
                keywords = routing_rules[dataset_type_lower]
                for keyword in keywords:
                    if keyword in question_lower:
                        score += 1
            
            # Also check column names for relevance
            for col in ds.columns:
                if col.name.lower() in question_lower:
                    score += 2  # Column name matches are stronger signals
            
            scores[ds.dataset_type] = score
        
        # Find dataset with highest score
        if scores:
            best_dataset_type = max(scores, key=scores.get)
            best_score = scores[best_dataset_type]
            
            logger.info(
                "Keyword-based routing for question '%s': scores=%s, chose '%s' (score=%d)",
                question,
                scores,
                best_dataset_type,
                best_score,
            )
            
            if best_score > 0:
                for ds in datasets:
                    if ds.dataset_type == best_dataset_type:
                        return ds
        
        # If no clear winner, return the first dataset (fallback)
        logger.warning(
            "No clear routing match for question '%s', using first available dataset: %s",
            question,
            datasets[0].dataset_type,
        )
        return datasets[0]

    def _get_dataset_description(self, dataset_type: str) -> str:
        """Get a human-readable description of what each dataset contains."""
        descriptions = {
            "sales": "Sales transactions, revenue, products sold, payment methods, customer purchases",
            "inventory": "Product stock levels, suppliers, reorder points, available quantities",
            "staff": "Employee information, roles, shifts, work schedules, team members",
            "transactions": "Financial transactions, payments, receipts",
            "customers": "Customer information, contact details, purchase history",
        }
        return descriptions.get(dataset_type.lower(), "Store data")


dataset_router = DatasetRouterService()

__all__ = ["dataset_router", "DatasetRouterService"]

