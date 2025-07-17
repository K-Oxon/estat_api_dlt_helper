"""DLT resource creation for e-Stat API data."""

from typing import Any, Callable, Optional

from ..config.models import EstatDltConfig


def create_estat_resource(
    config: EstatDltConfig,
    *,
    name: Optional[str] = None,
    primary_key: Optional[Any] = None,
    write_disposition: Optional[str] = None,
    columns: Optional[Any] = None,
    table_format: Optional[str] = None,
    file_format: Optional[str] = None,
    schema_contract: Optional[Any] = None,
    table_name: Optional[Callable[[Any], str]] = None,
    max_table_nesting: Optional[int] = None,
    selected: Optional[bool] = None,
    merge_key: Optional[Any] = None,
    parallelized: Optional[bool] = None,
    **resource_kwargs: Any,
) -> Any:  # Returns dlt.Resource
    """
    Create a DLT resource for e-Stat API data.

    This function creates a customizable DLT resource that fetches data
    from the e-Stat API based on the provided configuration.

    Args:
        config: Configuration for e-Stat API source and destination
        name: Resource name (defaults to table_name from config)
        primary_key: Primary key columns (overrides config if provided)
        write_disposition: Write disposition (overrides config if provided)
        columns: Column definitions for the resource
        table_format: Table format for certain destinations
        file_format: File format for filesystem destinations
        schema_contract: Schema contract settings
        table_name: Callable to generate dynamic table names
        max_table_nesting: Maximum nesting level for nested data
        selected: Whether this resource is selected for loading
        merge_key: Merge key for merge operations
        parallelized: Whether to parallelize this resource
        **resource_kwargs: Additional keyword arguments for dlt.resource

    Returns:
        dlt.Resource: Configured DLT resource for e-Stat API data

    Raises:
        NotImplementedError: This is just an interface, implementation pending

    Example:
        ```python
        from estat_api_dlt_helper import EstatDltConfig, create_estat_resource

        config = EstatDltConfig(...)
        resource = create_estat_resource(config)

        # Customize the resource
        resource = create_estat_resource(
            config,
            name="custom_stats",
            columns={"time": {"data_type": "timestamp"}},
            selected=True
        )
        ```
    """
    raise NotImplementedError("create_estat_resource implementation is pending")
