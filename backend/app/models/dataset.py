"""Pydantic models for dataset endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    name: str
    original_name: str
    sql_type: str
    pandas_dtype: str
    nullable: bool = True
    sample_values: List[str] = Field(default_factory=list)


class DatasetInfo(BaseModel):
    id: str
    display_name: str
    table_name: str
    original_filename: str
    row_count: int
    column_schema: List[ColumnSchema]
    sample_preview: List[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    notes: Optional[str] = None


class DatasetListResponse(BaseModel):
    datasets: List[DatasetInfo]


class DatasetPreviewResponse(BaseModel):
    columns: List[str]
    rows: List[dict[str, Any]]
    table_name: str

