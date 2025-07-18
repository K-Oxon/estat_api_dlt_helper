"""DLT pipeline creation for e-Stat API data."""

from typing import Any, Optional

import dlt

from ..config.models import EstatDltConfig
from ..utils.logging import get_logger

logger = get_logger(__name__)


def create_estat_pipeline(
    config: EstatDltConfig,
    *,
    pipeline_name: Optional[str] = None,
    pipelines_dir: Optional[str] = None,
    dataset_name: Optional[str] = None,
    import_schema_path: Optional[str] = None,
    export_schema_path: Optional[str] = None,
    dev_mode: Optional[bool] = None,
    refresh: Optional[str] = None,
    progress: Optional[str] = None,
    destination: Optional[Any] = None,
    staging: Optional[Any] = None,
    **pipeline_kwargs: Any,
) -> Any:  # dlt.Pipeline
    """
    Create a DLT pipeline for e-Stat API data loading.

    This function creates a customizable DLT pipeline configured for
    the specified destination based on the provided configuration.

    Args:
        config: Configuration for e-Stat API source and destination
        pipeline_name: Name of the pipeline (overrides config if provided)
        pipelines_dir: Directory to store pipeline state
        dataset_name: Dataset name in destination (overrides config if provided)
        import_schema_path: Path to import schema from
        export_schema_path: Path to export schema to
        dev_mode: Development mode (overrides config if provided)
        refresh: Schema refresh mode
        progress: Progress reporting configuration
        destination: DLT destination (constructed from config if not provided)
        staging: Staging destination for certain loaders
        **pipeline_kwargs: Additional keyword arguments for dlt.pipeline

    Returns:
        dlt.Pipeline: Configured DLT pipeline

    Example:
        ```python
        from estat_api_dlt_helper import EstatDltConfig, create_estat_pipeline

        config = EstatDltConfig(...)
        pipeline = create_estat_pipeline(config)

        # Customize the pipeline
        pipeline = create_estat_pipeline(
            config,
            pipeline_name="custom_estat_pipeline",
            dev_mode=True,
            progress="log"
        )
        ```
    """
    # Determine pipeline name
    name = pipeline_name or config.destination.pipeline_name
    if not name:
        # Generate default pipeline name
        stats_id = config.source.statsDataId
        if isinstance(stats_id, list):
            stats_id = "_".join(stats_id[:3])  # Limit to first 3 IDs
            if len(config.source.statsDataId) > 3:
                stats_id += "_etc"
        else:
            stats_id = stats_id

        name = f"estat_{config.destination.dataset_name}_{stats_id}"

    # Prepare destination configuration
    dest = destination or config.destination.destination

    # Handle destination-specific configurations
    if isinstance(dest, str):
        # String destination name
        if config.destination.credentials:
            # Create destination with credentials
            # For now, just use the string destination name
            # DLT will handle the destination creation internally
            pass

    # Prepare pipeline configuration
    pipeline_config = {
        "pipeline_name": name,
        "destination": dest,
        "dataset_name": dataset_name or config.destination.dataset_name,
    }

    # Add optional parameters with proper defaults
    if dev_mode is not None:
        pipeline_config["dev_mode"] = dev_mode
    elif config.destination.dev_mode is not None:
        pipeline_config["dev_mode"] = config.destination.dev_mode

    # Add other optional parameters
    optional_params = {
        "pipelines_dir": pipelines_dir,
        "import_schema_path": import_schema_path,
        "export_schema_path": export_schema_path,
        "refresh": refresh,
        "progress": progress,
        "staging": staging,
    }

    for key, value in optional_params.items():
        if value is not None:
            pipeline_config[key] = value

    # Add any additional pipeline kwargs
    pipeline_config.update(pipeline_kwargs)

    # Create and return the pipeline
    logger.info(
        f"Creating pipeline '{name}' for destination '{dest}' "
        f"with dataset '{pipeline_config['dataset_name']}'"
    )

    return dlt.pipeline(**pipeline_config)
