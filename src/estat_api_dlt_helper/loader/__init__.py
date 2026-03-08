"""Loader module for estat_api_dlt_helper."""

from .dlt_pipeline import create_estat_pipeline
from .dlt_resource import create_estat_resource
from .dlt_source import create_estat_source
from .estat_source import estat_source
from .estat_table import estat_table
from .load_manager import load_estat_data

__all__ = [
    "load_estat_data",
    "create_estat_resource",
    "create_estat_pipeline",
    "create_estat_source",
    "estat_source",
    "estat_table",
]
