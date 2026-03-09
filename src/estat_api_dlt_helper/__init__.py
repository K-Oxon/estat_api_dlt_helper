"""estat_api_dlt_helper - e-Stat API data loader using DLT."""

__version__ = "0.3.0"

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
    # API Client
    "EstatApiClient",
    # Parser
    "parse_response",
    # Main configuration
    "EstatDltConfig",
    "SourceConfig",
    "DestinationConfig",
    # Source / Resource
    "estat_source",
    "estat_table",
    # Loader functions
    "load_estat_data",
    "create_estat_resource",
    "create_unified_estat_resource",
    "create_estat_pipeline",
    "create_estat_source",
    # Version
    "__version__",
]
