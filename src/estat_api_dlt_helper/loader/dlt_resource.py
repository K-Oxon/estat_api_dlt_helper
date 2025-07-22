"""DLT resource creation for e-Stat API data."""

from typing import Any, Callable, Dict, Generator, Optional

import dlt
import pyarrow as pa

from ..api.client import EstatApiClient
from ..config.models import EstatDltConfig
from ..parser import parse_response
from ..utils.logging import get_logger

logger = get_logger(__name__)


def _create_api_params(config: EstatDltConfig) -> Dict[str, Any]:
    """Create API parameters from config."""
    params = {
        "lang": config.source.lang,
        "metaGetFlg": config.source.metaGetFlg,
        "cntGetFlg": config.source.cntGetFlg,
    }

    # Add optional parameters
    optional_params = [
        "explanationGetFlg",
        "annotationGetFlg",
        "replaceSpChars",
        "lvTab",
        "cdTab",
        "cdTabFrom",
        "cdTabTo",
        "lvTime",
        "cdTime",
        "cdTimeFrom",
        "cdTimeTo",
        "lvArea",
        "cdArea",
        "cdAreaFrom",
        "cdAreaTo",
    ]

    for param in optional_params:
        value = getattr(config.source, param, None)
        if value is not None:
            params[param] = value

    # Add extra parameters (e.g., cat01-cat15)
    if hasattr(config.source, "__pydantic_extra__"):
        extra = getattr(config.source, "__pydantic_extra__", {})
        if extra:
            params.update(extra)

    return params


def _fetch_estat_data(
    client: EstatApiClient,
    stats_data_id: str,
    params: Dict[str, Any],
    limit: int = 100000,
    maximum_offset: Optional[int] = None,
) -> Generator[pa.Table, None, None]:
    """Fetch data from e-Stat API and convert to Arrow format."""
    logger.info(f"Fetching data for stats_data_id: {stats_data_id}")

    # Use generator for pagination
    for response in client.get_stats_data_generator(
        stats_data_id=stats_data_id, limit_per_request=limit, **params
    ):
        try:
            # Parse response to Arrow table
            table = parse_response(response)

            if table is not None and len(table) > 0:
                yield table

                # Check if we've reached the maximum offset
                if maximum_offset:
                    result_info = (
                        response.get("GET_STATS_DATA", {})
                        .get("STATISTICAL_DATA", {})
                        .get("RESULT_INF", {})
                    )
                    to_number = int(result_info.get("TO_NUMBER", 0))
                    if to_number >= maximum_offset:
                        logger.info(f"Reached maximum offset: {maximum_offset}")
                        break

        except Exception as e:
            logger.error(f"Error processing response: {e}")
            raise


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
) -> Any:  # dlt.Resource
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
    # Prepare API parameters
    api_params = _create_api_params(config)

    # Get stats data IDs (ensure it's a list)
    stats_data_ids = config.source.statsDataId
    if isinstance(stats_data_ids, str):
        stats_data_ids = [stats_data_ids]

    # Prepare resource configuration
    resource_config: Dict[str, Any] = {
        "name": name or config.destination.table_name,
        "write_disposition": write_disposition or config.destination.write_disposition,
    }

    # Add primary key for merge disposition
    if primary_key is not None:
        resource_config["primary_key"] = primary_key
    elif (
        config.destination.write_disposition == "merge"
        and config.destination.primary_key
    ):
        pk = config.destination.primary_key
        if isinstance(pk, str):
            pk = [pk]
        resource_config["primary_key"] = pk

    # Add optional resource parameters
    optional_params = {
        "columns": columns,
        "table_format": table_format,
        "file_format": file_format,
        "schema_contract": schema_contract,
        "table_name": table_name,
        "max_table_nesting": max_table_nesting,
        "selected": selected,
        "merge_key": merge_key,
        "parallelized": parallelized,
    }

    for key, value in optional_params.items():
        if value is not None:
            resource_config[key] = value

    # Add any additional resource kwargs
    resource_config.update(resource_kwargs)

    @dlt.resource(**resource_config)  # type: ignore
    def estat_data() -> Generator[pa.Table, None, None]:
        """Generator function for e-Stat data."""
        client = EstatApiClient(app_id=config.source.app_id)

        try:
            # Process each stats data ID
            for stats_data_id in stats_data_ids:
                yield from _fetch_estat_data(
                    client=client,
                    stats_data_id=stats_data_id,
                    params=api_params,
                    limit=config.source.limit,
                    maximum_offset=config.source.maximum_offset,
                )
        finally:
            client.close()

    return estat_data()
