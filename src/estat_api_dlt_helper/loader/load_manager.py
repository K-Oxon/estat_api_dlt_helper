"""Load manager for e-Stat API data to DLT."""

from typing import Any, Dict, Optional

from ..config.models import EstatDltConfig


def load_estat_data(
    config: EstatDltConfig,
    *,
    credentials: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
    """
    Load e-Stat API data to the specified destination using DLT.

    This is a convenience function that creates and runs a DLT pipeline
    with the provided configuration.

    Args:
        config: Configuration for e-Stat API source and DLT destination
        credentials: Optional credentials to override destination credentials
        **kwargs: Additional arguments passed to pipeline.run()

    Raises:
        NotImplementedError: This is just an interface, implementation pending

    Example:
        ```python
        from estat_api_dlt_helper import EstatDltConfig, load_estat_data

        config = {
            "source": {
                "app_id": "YOUR_API_KEY",
                "statsDataId": "0000020211",
                "limit": 10
            },
            "destination": {
                "dwh": "duckdb",
                "dataset_name": "demo",
                "table_name": "demo",
                "write_disposition": "merge",
                "primary_key": ["time", "area", "cat01"]
            }
        }

        config = EstatDltConfig(**config)
        load_estat_data(config)
        ```
    """
    raise NotImplementedError("load_estat_data implementation is pending")
