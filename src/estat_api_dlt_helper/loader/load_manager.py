"""Load manager for e-Stat API data to DLT."""

from typing import Any, Dict, Optional


from ..config.models import EstatDltConfig
from ..utils.logging import get_logger
from .dlt_pipeline import create_estat_pipeline
from .dlt_resource import create_estat_resource

logger = get_logger(__name__)


def load_estat_data(
    config: EstatDltConfig,
    *,
    credentials: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Any:  # dlt.common.pipeline.LoadInfo
    """
    Load e-Stat API data to the specified destination using DLT.

    This is a convenience function that creates and runs a DLT pipeline
    with the provided configuration.

    Args:
        config: Configuration for e-Stat API source and DLT destination
        credentials: Optional credentials to override destination credentials
        **kwargs: Additional arguments passed to pipeline.run()

    Returns:
        LoadInfo object containing information about the load operation

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
                "destination": "duckdb",
                "dataset_name": "demo",
                "table_name": "demo",
                "write_disposition": "merge",
                "primary_key": ["time", "area", "cat01"]
            }
        }

        config = EstatDltConfig(**config)
        info = load_estat_data(config)
        print(info)
        ```
    """
    logger.info("Starting e-Stat data load process")

    try:
        # Override credentials if provided
        if credentials:
            config.destination.credentials = credentials

        # Create the resource
        logger.debug("Creating e-Stat resource")
        resource = create_estat_resource(config)

        # Create the pipeline
        logger.debug("Creating DLT pipeline")
        pipeline = create_estat_pipeline(config)

        # Run the pipeline
        logger.info(
            f"Running pipeline for stats_data_id: {config.source.statsDataId} "
            f"to {config.destination.destination}/{config.destination.dataset_name}/"
            f"{config.destination.table_name}"
        )

        info = pipeline.run(resource, **kwargs)

        # Log results
        logger.info(f"Load completed: {info}")

        return info

    except Exception as e:
        logger.error(f"Error during data load: {e}")
        raise
