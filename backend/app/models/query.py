from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class QueryResultModel(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    returned_rows: int
    truncated: bool = False


class VisualizationSuggestionModel(BaseModel):
    type: str
    config: Dict[str, Any]


class NL2SQLRequest(BaseModel):
    question: str
    store_id: Optional[str] = None
    dataset_type: Optional[str] = None


class NL2SQLResponse(BaseModel):
    question: str
    store_id: str
    dataset_type: Optional[str] = None
    sql: Optional[str] = None
    error: Optional[str] = None
    result: Optional[QueryResultModel] = None
    explanation: Optional[str] = None
    visualization: Optional[VisualizationSuggestionModel] = None


class SQLExecuteRequest(BaseModel):
    store_id: Optional[str] = None
    sql: str


class SQLExecuteResponse(BaseModel):
    store_id: str
    sql: str
    result: QueryResultModel


class SQLValidationResponse(BaseModel):
    is_valid: bool
    error: Optional[str] = None
