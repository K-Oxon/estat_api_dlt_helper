"""estat_api_dlt_helper - e-Stat API data loader using DLT."""

__version__ = "0.3.2"

from .api.client import EstatApiClient
from .config import DestinationConfig, EstatDltConfig, SourceConfig
from .loader import (
    create_estat_pipeline,
    create_estat_resource,
    create_estat_source,
    estat_source,
    estat_table,
    load_estat_data,
)
from .loader.unified_schema_resource import create_unified_estat_resource
from .parser import parse_response

__all__ = [
    "DestinationConfig",
    "EstatApiClient",
    "EstatDltConfig",
    "SourceConfig",
    "__version__",
    "create_estat_pipeline",
    "create_estat_resource",
    "create_estat_source",
    "create_unified_estat_resource",
    "estat_source",
    "estat_table",
    "load_estat_data",
    "parse_response",
]
