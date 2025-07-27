"""estat_api_dlt_helper - e-Stat API data loader using DLT."""

__version__ = "0.1.2"

from .api.client import EstatApiClient
from .config import DestinationConfig, EstatDltConfig, SourceConfig
from .loader import create_estat_pipeline, create_estat_resource, load_estat_data
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
    # Loader functions
    "load_estat_data",
    "create_estat_resource",
    "create_estat_pipeline",
    # Version
    "__version__",
]
