"""Pydantic models for NL2SQL endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NLQRequest(BaseModel):
    question: str = Field(..., description="Natural language question")
    store_id: Optional[str] = Field(
        default=None, description="Store identifier (defaults to demo-store)"
    )
    dataset_type: Optional[str] = Field(
        default=None,
        description="Specific dataset to target (sales, inventory, staff, transactions)",
    )
    locale: Optional[str] = Field(
        default=None, description="Preferred locale code (e.g., 'ml', 'en')"
    )


class NLQVisualization(BaseModel):
    type: str
    config: Dict[str, Any] = Field(default_factory=dict)


class NLQResponse(BaseModel):
    sql: str
    columns: List[str]
    rows: List[List[Any]]
    executed_sql: str
    explanations: Dict[str, str]
    warnings: List[str] = Field(default_factory=list)
    visualization: Optional[NLQVisualization] = None

