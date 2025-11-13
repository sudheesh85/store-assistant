from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.settings import settings
from app.services.dataset_manager import DatasetMetadata, dataset_manager
from app.services.explanation import default_explanation_service
from app.services.query_executor import query_executor
from app.services.sql_generator import sql_generator
from app.services.visualization import default_visualizer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ask", tags=["Ask"])


class AskDataModel(BaseModel):
    columns: List[str]
    rows: List[List[Any]]


class AskRequestModel(BaseModel):
    question: str
    dataset_type: Optional[str] = None
    store_id: Optional[str] = None
    org_id: Optional[int] = None
    session_id: Optional[str] = None


class AskResponseModel(BaseModel):
    success: bool
    response: str
    sql: Optional[str] = None
    data: Optional[AskDataModel] = None
    visualization: Optional[str] = None
    error: Optional[str] = None


def _parse_timestamp(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.min


def _resolve_store_id(store_id: Optional[str]) -> str:
    return store_id or settings.DEFAULT_STORE_ID


def _resolve_dataset(
    store_id: str, dataset_type: Optional[str]
) -> Optional[DatasetMetadata]:
    if dataset_type:
        try:
            return dataset_manager.get_dataset(store_id, dataset_type)
        except KeyError:
            logger.warning("Dataset %s not found for store %s", dataset_type, store_id)
            return None

    datasets = dataset_manager.list_datasets(store_id)
    if not datasets:
        return None

    # Pick the most recently uploaded dataset as a sensible default.
    return max(datasets, key=lambda ds: _parse_timestamp(ds.uploaded_at))


def _map_visualization(suggestion: Optional[Dict[str, Any]]) -> Optional[str]:
    if not suggestion:
        return None
    viz_type = suggestion.get("type")
    mapping = {
        "bar": "bar",
        "bar_horizontal": "bar",
        "pie": "pie",
        "line": "line",
        "area_chart": "line",
        "metric": "table",
        "table": "table",
    }
    return mapping.get(viz_type)


def _process_question(payload: AskRequestModel) -> AskResponseModel:
    store_id = _resolve_store_id(payload.store_id)
    dataset = _resolve_dataset(store_id, payload.dataset_type)
    if dataset is None:
        return AskResponseModel(
            success=False,
            response="",
            error="No datasets available. Please upload a CSV before asking questions.",
        )

    sql_query, generation_error = sql_generator.generate_sql(payload.question, dataset)
    if generation_error or not sql_query:
        return AskResponseModel(
            success=False,
            response="",
            error=generation_error or "Unable to generate SQL for this question.",
        )

    try:
        execution = query_executor.execute(store_id, sql_query)
    except ValueError as exc:
        return AskResponseModel(
            success=False,
            response="",
            sql=sql_query,
            error=str(exc),
        )
    except Exception as exc:
        logger.exception("Query execution failed")
        return AskResponseModel(
            success=False,
            response="",
            sql=sql_query,
            error="Failed to execute query.",
        )

    data_payload = AskDataModel(columns=execution["columns"], rows=execution["rows"])

    explanation_text = "Query executed successfully."
    if settings.ENABLE_RESULT_EXPLANATION:
        try:
            explanation_candidate = default_explanation_service.generate(
                payload.question,
                execution["columns"],
                execution["rows"],
            )
            if explanation_candidate and "OPENAI_API_KEY" not in explanation_candidate:
                explanation_text = explanation_candidate
        except Exception as exc:
            logger.warning("Explanation generation failed: %s", exc)

    visualization = None
    if settings.ENABLE_VISUALIZATION_SUGGESTIONS:
        try:
            suggestion = default_visualizer.suggest(
                payload.question,
                execution["columns"],
                execution["rows"],
            )
            visualization = _map_visualization(suggestion)
        except Exception as exc:
            logger.warning("Visualization suggestion failed: %s", exc)

    return AskResponseModel(
        success=True,
        response=explanation_text,
        sql=sql_query,
        data=data_payload,
        visualization=visualization,
    )


def _sse_event(payload: Dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/question", response_model=AskResponseModel)
async def ask_question(payload: AskRequestModel) -> AskResponseModel:
    """Handle non-streaming NLQ requests (compatibility endpoint for frontend)."""
    return _process_question(payload)


@router.post("/question/stream")
async def ask_question_stream(payload: AskRequestModel) -> StreamingResponse:
    """Stream NLQ responses using Server-Sent Events."""

    async def event_generator() -> AsyncIterator[str]:
        result = _process_question(payload)
        if not result.success:
            yield _sse_event({
                "type": "error",
                "message": result.error or "Unable to answer question.",
            })
            return

        yield _sse_event({
            "type": "chunk",
            "text": result.response,
        })

        metadata_event: Dict[str, Any] = {
            "type": "metadata",
            "success": True,
        }
        if result.data:
            metadata_event["columns"] = result.data.columns
            metadata_event["rows"] = result.data.rows
        if result.visualization:
            metadata_event["visualization"] = result.visualization
        yield _sse_event(metadata_event)

        yield _sse_event({
            "type": "complete",
            "text": result.response,
            "response": result.response,
            "sql": result.sql,
            "data": result.data.dict() if result.data else None,
            "visualization": result.visualization,
        })

    return StreamingResponse(event_generator(), media_type="text/event-stream")
