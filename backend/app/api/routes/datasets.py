from __future__ import annotations

import io
import json
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from app.core.settings import settings
from app.models import (
    DatasetDeleteResponse,
    DatasetListResponse,
    DatasetMetadataModel,
    DatasetSchemaResponse,
    DatasetUploadResponse,
)
from app.services.dataset_manager import DatasetMetadata, dataset_manager

router = APIRouter(tags=["datasets"], prefix="/datasets")
logger = logging.getLogger(__name__)


def _coerce_store_id(store_id: Optional[str]) -> str:
    return store_id or settings.DEFAULT_STORE_ID


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    dataset_type: str = Form(...),
    file: UploadFile = File(...),
    column_descriptions: Optional[str] = Form(None),
    store_id: Optional[str] = Form(None),
) -> DatasetUploadResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB limit",
        )

    buffer = io.BytesIO(contents)
    try:
        dataframe = pd.read_csv(buffer)
    except Exception as exc:
        logger.error("Failed to parse CSV: %s", exc)
        raise HTTPException(status_code=400, detail="Unable to parse CSV file") from exc

    descriptions_dict: Optional[dict[str, str]] = None
    if column_descriptions:
        try:
            descriptions_dict = json.loads(column_descriptions)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail="column_descriptions must be valid JSON",
            ) from exc

    target_store_id = _coerce_store_id(store_id)

    try:
        metadata = dataset_manager.upsert_dataset(
            store_id=target_store_id,
            dataset_type=dataset_type,
            dataframe=dataframe,
            source_file=file.filename,
            column_descriptions=descriptions_dict,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Dataset ingestion failed")
        raise HTTPException(status_code=500, detail="Failed to store dataset") from exc

    return DatasetUploadResponse(dataset=_to_model(metadata))


@router.get("", response_model=DatasetListResponse)
async def list_datasets(store_id: Optional[str] = Query(None)) -> DatasetListResponse:
    target_store_id = _coerce_store_id(store_id)
    datasets = [
        _to_model(ds) for ds in dataset_manager.list_datasets(target_store_id)
    ]
    return DatasetListResponse(store_id=target_store_id, datasets=datasets)


@router.get("/{dataset_type}", response_model=DatasetSchemaResponse)
async def get_dataset(dataset_type: str, store_id: Optional[str] = Query(None)) -> DatasetSchemaResponse:
    target_store_id = _coerce_store_id(store_id)
    try:
        metadata = dataset_manager.get_dataset(target_store_id, dataset_type)
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    schema_text = dataset_manager.get_schema_description(target_store_id, dataset_type)
    return DatasetSchemaResponse(dataset=_to_model(metadata), schema_text=schema_text)


@router.delete("/{dataset_type}", response_model=DatasetDeleteResponse)
async def delete_dataset(dataset_type: str, store_id: Optional[str] = Query(None)) -> DatasetDeleteResponse:
    target_store_id = _coerce_store_id(store_id)
    dataset_manager.delete_dataset(target_store_id, dataset_type)
    return DatasetDeleteResponse(success=True, dataset_type=dataset_type)


def _to_model(metadata: DatasetMetadata) -> DatasetMetadataModel:
    return DatasetMetadataModel(
        dataset_type=metadata.dataset_type,
        table_name=metadata.table_name,
        row_count=metadata.row_count,
        source_file=metadata.source_file,
        uploaded_at=datetime.fromisoformat(metadata.uploaded_at),
        columns=[
            {
                "name": column.name,
                "original_name": column.original_name,
                "dtype": column.dtype,
                "description": column.description,
                "sample_values": column.sample_values,
            }
            for column in metadata.columns
        ],
    )
