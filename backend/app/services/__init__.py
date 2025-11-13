"""Service singletons for convenience imports."""

from .dataset_manager import dataset_manager
from .explanation import default_explanation_service
from .query_executor import query_executor
from .sql_generator import sql_generator
from .visualization import default_visualizer

__all__ = [
    "dataset_manager",
    "default_explanation_service",
    "query_executor",
    "sql_generator",
    "default_visualizer",
]

