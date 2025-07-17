"""Loader module for estat_api_dlt_helper."""

from .dlt_pipeline import create_estat_pipeline
from .dlt_resource import create_estat_resource
from .load_manager import load_estat_data

__all__ = [
    "load_estat_data",
    "create_estat_resource",
    "create_estat_pipeline",
]
