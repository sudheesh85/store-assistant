from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_numeric_dtype
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core.settings import settings
from app.metadata.column_defaults import merge_descriptions
from app.utils.strings import ensure_unique_names, normalize_column_name

logger = logging.getLogger(__name__)

VALID_DATASET_TYPES = {"sales", "inventory", "staff", "transactions"}


@dataclass
class ColumnMetadata:
    name: str
    original_name: str
    dtype: str
    description: Optional[str]
    sample_values: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "original_name": self.original_name,
            "dtype": self.dtype,
            "description": self.description,
            "sample_values": self.sample_values,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ColumnMetadata":
        return cls(
            name=payload["name"],
            original_name=payload.get("original_name", payload["name"]),
            dtype=payload.get("dtype", "text"),
            description=payload.get("description"),
            sample_values=payload.get("sample_values", []),
        )


@dataclass
class DatasetMetadata:
    store_id: str
    dataset_type: str
    table_name: str
    row_count: int
    source_file: Optional[str]
    uploaded_at: str
    columns: List[ColumnMetadata]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "store_id": self.store_id,
            "dataset_type": self.dataset_type,
            "table_name": self.table_name,
            "row_count": self.row_count,
            "source_file": self.source_file,
            "uploaded_at": self.uploaded_at,
            "columns": [column.to_dict() for column in self.columns],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DatasetMetadata":
        columns = [ColumnMetadata.from_dict(col) for col in payload.get("columns", [])]
        return cls(
            store_id=payload.get("store_id", settings.DEFAULT_STORE_ID),
            dataset_type=payload["dataset_type"],
            table_name=payload["table_name"],
            row_count=payload.get("row_count", 0),
            source_file=payload.get("source_file"),
            uploaded_at=payload.get("uploaded_at", datetime.utcnow().isoformat()),
            columns=columns,
        )


class DatasetManager:
    """Manages dataset ingestion, metadata registry, and SQLite engines per store."""

    def __init__(self) -> None:
        self.registry_path = settings.DATA_STORAGE_PATH / "datasets_registry.json"
        self.store_base_path = settings.DATA_STORAGE_PATH / "stores"
        self.store_base_path.mkdir(parents=True, exist_ok=True)
        self.engine_cache: dict[str, Engine] = {}
        self.registry: dict[str, dict[str, DatasetMetadata]] = {}
        self._load_registry()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def upsert_dataset(
        self,
        *,
        store_id: str,
        dataset_type: str,
        dataframe: pd.DataFrame,
        source_file: Optional[str],
        column_descriptions: Optional[Dict[str, str]] = None,
    ) -> DatasetMetadata:
        if dataset_type not in VALID_DATASET_TYPES:
            raise ValueError(
                f"Unknown dataset_type '{dataset_type}'. Allowed: {sorted(VALID_DATASET_TYPES)}"
            )
        if dataframe.empty:
            raise ValueError("Uploaded CSV has no rows")

        sanitized_df, column_mapping = self._sanitize_dataframe(dataframe)
        row_count = len(sanitized_df)

        table_name = f"{dataset_type}_raw"
        engine = self._get_engine(store_id)

        logger.info(
            "Writing %s dataset for store %s into table %s (%d rows)",
            dataset_type,
            store_id,
            table_name,
            row_count,
        )
        
        # For now, use replace mode (original behavior)
        # TODO: Enable append mode with metadata columns in future version
        with engine.begin() as connection:
            sanitized_df.to_sql(table_name, connection, if_exists="replace", index=False)

        merged_descriptions = merge_descriptions(dataset_type, column_descriptions)
        columns_metadata = self._build_columns_metadata(
            sanitized_df, column_mapping, merged_descriptions
        )

        metadata = DatasetMetadata(
            store_id=store_id,
            dataset_type=dataset_type,
            table_name=table_name,
            row_count=row_count,
            source_file=source_file,
            uploaded_at=datetime.utcnow().isoformat(),
            columns=columns_metadata,
        )

        store_registry = self.registry.setdefault(store_id, {})
        store_registry[dataset_type] = metadata
        self._persist_registry()

        return metadata

    def list_datasets(self, store_id: str) -> List[DatasetMetadata]:
        store_registry = self.registry.get(store_id, {})
        return list(store_registry.values())

    def get_dataset(self, store_id: str, dataset_type: str) -> DatasetMetadata:
        store_registry = self.registry.get(store_id, {})
        if dataset_type not in store_registry:
            raise KeyError(f"Dataset {dataset_type} not found for store {store_id}")
        return store_registry[dataset_type]

    def delete_dataset(self, store_id: str, dataset_type: str) -> None:
        store_registry = self.registry.get(store_id, {})
        if dataset_type not in store_registry:
            return
        table_name = f"{dataset_type}_raw"
        engine = self._get_engine(store_id)
        try:
            with engine.begin() as connection:
                connection.exec_driver_sql(f"DROP TABLE IF EXISTS {table_name}")
        except Exception as exc:
            logger.warning("Failed to drop table %s for store %s: %s", table_name, store_id, exc)
        del store_registry[dataset_type]
        if not store_registry:
            self.registry.pop(store_id, None)
        self._persist_registry()

    def get_schema_description(self, store_id: str, dataset_type: str) -> str:
        metadata = self.get_dataset(store_id, dataset_type)
        lines = [f"Table: {metadata.table_name}"]
        for column in metadata.columns:
            example = ""
            if column.sample_values:
                preview = ", ".join(str(v) for v in column.sample_values[:3])
                example = f" (examples: {preview})"
            description = f" – {column.description}" if column.description else ""
            lines.append(f"- {column.name} [{column.dtype}]{description}{example}")
        return "\n".join(lines)

    def get_engine_for_store(self, store_id: str) -> Engine:
        return self._get_engine(store_id)

    # ------------------------------------------------------------------
    # Registry helpers
    # ------------------------------------------------------------------
    def _load_registry(self) -> None:
        if not self.registry_path.exists():
            logger.info("Dataset registry not found, creating new file at %s", self.registry_path)
            self.registry_path.write_text("{}", encoding="utf-8")
            return
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            for store_id, datasets in data.items():
                if not isinstance(datasets, dict):
                    logger.warning("Skipping malformed registry entry for store %s", store_id)
                    continue
                parsed: dict[str, DatasetMetadata] = {}
                for dataset_type, metadata in datasets.items():
                    if not isinstance(metadata, dict):
                        logger.warning(
                            "Skipping malformed dataset metadata for store %s (%s)",
                            store_id,
                            dataset_type,
                        )
                        continue
                    try:
                        parsed[dataset_type] = DatasetMetadata.from_dict(metadata)
                    except KeyError:
                        logger.warning(
                            "Skipping legacy dataset metadata for store %s (%s)",
                            store_id,
                            dataset_type,
                        )
                if parsed:
                    self.registry[store_id] = parsed
        except Exception as exc:
            logger.error("Failed to load dataset registry: %s", exc, exc_info=True)
            self.registry = {}

    def _persist_registry(self) -> None:
        payload = {
            store_id: {
                dataset_type: metadata.to_dict()
                for dataset_type, metadata in datasets.items()
            }
            for store_id, datasets in self.registry.items()
        }
        self.registry_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _sanitize_dataframe(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, Dict[str, str]]:
        df_copy = df.copy()
        normalized_columns = [normalize_column_name(col) for col in df_copy.columns]
        normalized_columns = ensure_unique_names(normalized_columns)
        mapping = dict(zip(df_copy.columns, normalized_columns))
        df_copy = df_copy.rename(columns=mapping)

        for column in df_copy.columns:
            series = df_copy[column]
            if is_bool_dtype(series):
                df_copy[column] = series.astype(int)
            elif is_datetime64_any_dtype(series):
                df_copy[column] = series.dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")
            else:
                df_copy[column] = series.where(pd.notna(series), None)
        return df_copy, mapping

    def _build_columns_metadata(
        self,
        df: pd.DataFrame,
        mapping: Dict[str, str],
        description_map: Dict[str, str],
    ) -> List[ColumnMetadata]:
        columns: List[ColumnMetadata] = []
        for original_name, normalized in mapping.items():
            series = df[normalized]
            columns.append(
                ColumnMetadata(
                    name=normalized,
                    original_name=original_name,
                    dtype=self._human_readable_dtype(series),
                    description=description_map.get(normalized),
                    sample_values=self._sample_column_values(series),
                )
            )
        return columns

    def _human_readable_dtype(self, series: pd.Series) -> str:
        if is_bool_dtype(series):
            return "boolean"
        if is_numeric_dtype(series):
            return "number"
        if is_datetime64_any_dtype(series):
            return "datetime"
        return "text"

    def _sample_column_values(self, series: pd.Series, max_samples: int = 5) -> List[Any]:
        try:
            unique_values = series.dropna().unique().tolist()
        except Exception:
            unique_values = []
        samples: List[Any] = []
        for value in unique_values[:max_samples]:
            if isinstance(value, (datetime, pd.Timestamp)):
                samples.append(str(value))
            else:
                samples.append(value)
        return samples

    def _store_db_path(self, store_id: str) -> Path:
        return self.store_base_path / f"{store_id}.db"

    def _get_engine(self, store_id: str) -> Engine:
        if store_id in self.engine_cache:
            return self.engine_cache[store_id]
        db_path = self._store_db_path(store_id)
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            future=True,
        )
        self.engine_cache[store_id] = engine
        return engine


dataset_manager = DatasetManager()

__all__ = [
    "dataset_manager",
    "DatasetManager",
    "DatasetMetadata",
    "ColumnMetadata",
    "VALID_DATASET_TYPES",
]
