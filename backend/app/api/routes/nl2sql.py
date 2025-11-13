from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.core.settings import settings
from app.models import (
    NL2SQLRequest,
    NL2SQLResponse,
    QueryResultModel,
    VisualizationSuggestionModel,
)
from app.services.dataset_manager import DatasetMetadata, dataset_manager
from app.services.explanation import default_explanation_service
from app.services.query_executor import query_executor
from app.services.sql_generator import sql_generator
from app.services.visualization import default_visualizer

router = APIRouter(tags=["nl2sql"], prefix="/nl2sql")
logger = logging.getLogger(__name__)


def _resolve_store_id(store_id: str | None) -> str:
    return store_id or settings.DEFAULT_STORE_ID


def _pick_dataset_metadata(store_id: str, requested_type: str | None) -> DatasetMetadata:
    if requested_type:
        try:
            return dataset_manager.get_dataset(store_id, requested_type)
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset '{requested_type}' not found for store {store_id}",
            )

    store_datasets = dataset_manager.list_datasets(store_id)
    if not store_datasets:
        raise HTTPException(
            status_code=400,
            detail="No datasets uploaded for this store. Upload CSVs before asking questions.",
        )
    if len(store_datasets) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple datasets available; please specify dataset_type in the request.",
        )
    return store_datasets[0]


@router.post("/ask", response_model=NL2SQLResponse)
async def nl2sql_ask(payload: NL2SQLRequest) -> NL2SQLResponse:
    store_id = _resolve_store_id(payload.store_id)
    dataset = _pick_dataset_metadata(store_id, payload.dataset_type)

    sql_query, error = sql_generator.generate_sql(payload.question, dataset)
    if error or not sql_query:
        return NL2SQLResponse(
            question=payload.question,
            store_id=store_id,
            dataset_type=dataset.dataset_type,
            error=error or "Unable to generate SQL",
        )

    try:
        result_data = query_executor.execute(store_id, sql_query)
    except ValueError as exc:
        return NL2SQLResponse(
            question=payload.question,
            store_id=store_id,
            dataset_type=dataset.dataset_type,
            sql=sql_query,
            error=str(exc),
        )
    except Exception as exc:
        logger.error("NL2SQL query execution failed: %s", exc, exc_info=True)
        return NL2SQLResponse(
            question=payload.question,
            store_id=store_id,
            dataset_type=dataset.dataset_type,
            sql=sql_query,
            error="Query execution failed",
        )

    explanation_text = None
    if settings.ENABLE_RESULT_EXPLANATION:
        explanation_text = default_explanation_service.generate(
            payload.question,
            result_data["columns"],
            result_data["rows"],
        )

    visualization_payload = None
    if settings.ENABLE_VISUALIZATION_SUGGESTIONS:
        suggestion = default_visualizer.suggest(
            payload.question,
            result_data["columns"],
            result_data["rows"],
        )
        if suggestion:
            viz_type = suggestion.get("type", "custom")
            config = {key: value for key, value in suggestion.items() if key != "type"}
            visualization_payload = VisualizationSuggestionModel(type=viz_type, config=config)

    result_model = QueryResultModel(**result_data)
    return NL2SQLResponse(
        question=payload.question,
        store_id=store_id,
        dataset_type=dataset.dataset_type,
        sql=sql_query,
        result=result_model,
        explanation=explanation_text,
        visualization=visualization_payload,
    )
