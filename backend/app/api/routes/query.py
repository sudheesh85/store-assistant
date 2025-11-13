from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.core.settings import settings
from app.models import (
    QueryResultModel,
    SQLExecuteRequest,
    SQLExecuteResponse,
    SQLValidationResponse,
)
from app.services.dataset_manager import dataset_manager
from app.services.query_executor import query_executor

router = APIRouter(tags=["query"], prefix="/query")
logger = logging.getLogger(__name__)


def _resolve_store_id(store_id: str | None) -> str:
    return store_id or settings.DEFAULT_STORE_ID


def _ensure_store_has_data(store_id: str) -> None:
    datasets = dataset_manager.list_datasets(store_id)
    if not datasets:
        raise HTTPException(
            status_code=400,
            detail="No datasets uploaded for this store. Upload CSVs before querying.",
        )


@router.post("/execute", response_model=SQLExecuteResponse)
async def execute_sql(payload: SQLExecuteRequest) -> SQLExecuteResponse:
    store_id = _resolve_store_id(payload.store_id)
    _ensure_store_has_data(store_id)

    try:
        result_data = query_executor.execute(store_id, payload.sql)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("SQL execution failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to execute query") from exc

    result_model = QueryResultModel(**result_data)
    return SQLExecuteResponse(store_id=store_id, sql=payload.sql, result=result_model)


@router.post("/validate", response_model=SQLValidationResponse)
async def validate_sql(payload: SQLExecuteRequest) -> SQLValidationResponse:
    store_id = _resolve_store_id(payload.store_id)
    _ensure_store_has_data(store_id)

    try:
        query_executor._assert_read_only(payload.sql)
    except ValueError as exc:
        return SQLValidationResponse(is_valid=False, error=str(exc))

    return SQLValidationResponse(is_valid=True)
