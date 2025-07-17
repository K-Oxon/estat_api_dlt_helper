"""DLT pipeline creation for e-Stat API data."""

from typing import Any, Optional

from ..config.models import EstatDltConfig


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
) -> Any:  # Returns dlt.Pipeline
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

    Raises:
        NotImplementedError: This is just an interface, implementation pending

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
    raise NotImplementedError("create_estat_pipeline implementation is pending")
