from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DatasetColumnModel(BaseModel):
    name: str
    original_name: str
    dtype: str
    description: Optional[str] = None
    sample_values: List[str | int | float | None] = Field(default_factory=list)


class DatasetMetadataModel(BaseModel):
    dataset_type: str
    table_name: str
    row_count: int
    source_file: Optional[str] = None
    uploaded_at: datetime
    columns: List[DatasetColumnModel]


class DatasetUploadResponse(BaseModel):
    dataset: DatasetMetadataModel


class DatasetListResponse(BaseModel):
    store_id: str
    datasets: List[DatasetMetadataModel]


class DatasetSchemaResponse(BaseModel):
    dataset: DatasetMetadataModel
    schema_text: str


class DatasetDeleteResponse(BaseModel):
    success: bool
    dataset_type: str


class DatasetUploadRequest(BaseModel):
    name: Optional[str] = None
    dataset_type: str
    column_descriptions: Optional[dict[str, str]] = None
    store_id: Optional[str] = None
