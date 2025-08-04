"""DLT resource with unified schema for handling different metadata structures.

This module provides a solution to the "Schema at index X was different" error
that occurs when loading multiple e-Stat API datasets with varying metadata
structures into a single DLT pipeline.

Background:
    When fetching data from multiple statsDataIds, the e-Stat API may return
    different metadata structures. For example, some datasets include a
    'parent_code' field in their time_metadata, while others don't. This
    causes PyArrow to fail when concatenating tables due to schema mismatches.

Solution:
    This module implements a unified schema approach using Pydantic models
    that define the superset of all possible fields. Missing fields are
    automatically set to None, ensuring consistent schema across all datasets.

Key Features:
    - Unified Pydantic models for all metadata types
    - Automatic handling of missing fields
    - Efficient PyArrow-native processing (no pandas dependency)
    - Batch processing for optimal memory usage
    - Support for unknown fields via extra_dimensions and extra_metadata

Example:
    >>> from estat_api_dlt_helper import EstatDltConfig
    >>> from estat_api_dlt_helper.loader.unified_schema_resource import create_unified_estat_resource
    >>>
    >>> config = EstatDltConfig(
    ...     source={"statsDataId": ["0004028473", "0004028474", "0004028475"]},
    ...     destination={"table_name": "unified_stats"}
    ... )
    >>>
    >>> # Use unified schema resource instead of regular resource
    >>> resource = create_unified_estat_resource(config)
    >>> pipeline.run(resource)  # No schema errors!
"""

from collections import OrderedDict
from typing import Any, Callable, Dict, Generator, Optional

import dlt
import pyarrow as pa
from pydantic import ValidationError

from ..api.client import EstatApiClient
from ..config.models import EstatDltConfig
from ..models.unified_schema import (
    UnifiedAreaMetadata,
    UnifiedCategoryMetadata,
    UnifiedEstatRecord,
    UnifiedStatInf,
    UnifiedTabMetadata,
    UnifiedTimeMetadata,
)
from ..utils.logging import get_logger

logger = get_logger(__name__)


def _convert_to_unified_metadata(
    field_name: str, metadata_dict: Dict[str, Any]
) -> Optional[Any]:
    """Convert metadata dictionary to unified metadata model."""
    if not metadata_dict:
        return None

    try:
        if field_name == "time":
            return UnifiedTimeMetadata(**metadata_dict)
        elif field_name == "area":
            return UnifiedAreaMetadata(**metadata_dict)
        elif field_name == "tab":
            return UnifiedTabMetadata(**metadata_dict)
        elif field_name.startswith("cat"):
            return UnifiedCategoryMetadata(**metadata_dict)
        else:
            # Generic category metadata for unknown field types
            return UnifiedCategoryMetadata(**metadata_dict)
    except ValidationError as e:
        logger.warning(f"Failed to convert {field_name} metadata: {e}")
        return None


def _convert_arrow_to_unified_records(
    arrow_table: pa.Table,
) -> Generator[Dict[str, Any], None, None]:
    """Convert Arrow table to unified records using native PyArrow operations.

    This optimized version avoids pandas conversion and uses efficient
    batch processing for better performance with large datasets.
    Returns dictionaries with preserved column order.
    """

    # Pre-analyze column types once to avoid repeated checks
    # IMPORTANT: Preserve the original column order from arrow_table
    metadata_columns = {}
    dimension_columns = []
    known_columns = set(UnifiedEstatRecord.model_fields.keys())
    extra_dimension_columns = []

    # Store original column order for preserving sequence
    original_column_order = list(arrow_table.column_names)

    for col_name in original_column_order:  # Use original order
        if col_name.endswith("_metadata"):
            field_name = col_name.replace("_metadata", "")
            metadata_columns[col_name] = field_name
        elif col_name in known_columns:
            dimension_columns.append(col_name)
        elif col_name != "stat_inf" and not col_name.endswith("_metadata"):
            extra_dimension_columns.append(col_name)

    # Process in batches for better memory efficiency
    batch_size = 1000
    num_rows = len(arrow_table)

    for batch_start in range(0, num_rows, batch_size):
        batch_end = min(batch_start + batch_size, num_rows)
        batch_table = arrow_table.slice(batch_start, batch_end - batch_start)

        # Convert batch to dictionaries using pyarrow (much faster than pandas)
        batch_dicts = batch_table.to_pylist()

        for row_dict in batch_dicts:
            # Use OrderedDict to preserve column order
            record_data = OrderedDict()
            extra_dimensions = OrderedDict()
            extra_metadata = OrderedDict()

            # Process columns in their original order
            for col_name in original_column_order:
                if col_name not in row_dict or row_dict[col_name] is None:
                    continue

                value = row_dict[col_name]

                # Handle different column types
                if col_name == "stat_inf":
                    try:
                        record_data[col_name] = UnifiedStatInf(**value)
                    except (ValidationError, TypeError) as e:
                        logger.warning(f"Failed to convert stat_inf: {e}")
                        continue
                elif col_name.endswith("_metadata"):
                    field_name = metadata_columns.get(col_name)
                    if isinstance(value, dict) and field_name:
                        unified_metadata = _convert_to_unified_metadata(
                            field_name, value
                        )
                        if unified_metadata is not None:
                            record_data[col_name] = unified_metadata
                        else:
                            extra_metadata[col_name] = value
                    else:
                        extra_metadata[col_name] = value
                elif col_name in known_columns:
                    record_data[col_name] = value
                else:
                    extra_dimensions[col_name] = value

            # Add extra fields if any
            if extra_dimensions:
                record_data["extra_dimensions"] = extra_dimensions
            if extra_metadata:
                record_data["extra_metadata"] = extra_metadata

            try:
                # Validate with UnifiedEstatRecord but yield the ordered dict
                UnifiedEstatRecord(**record_data)  # Validate only
                yield dict(record_data)  # Convert OrderedDict to dict for DLT
            except ValidationError as e:
                logger.warning(f"Failed to create unified record: {e}")
                continue


def _fetch_unified_estat_data(
    client: EstatApiClient,
    stats_data_id: str,
    params: Dict[str, Any],
    limit: int = 100000,
    maximum_offset: Optional[int] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Fetch data from e-Stat API and convert to unified records."""
    logger.info(f"Fetching unified data for stats_data_id: {stats_data_id}")

    # Import here to avoid circular import
    from ..parser import parse_response

    # Use generator for pagination
    for response in client.get_stats_data_generator(
        stats_data_id=stats_data_id, limit_per_request=limit, **params
    ):
        try:
            # Parse response to Arrow table first
            arrow_table = parse_response(response)

            if arrow_table is not None and len(arrow_table) > 0:
                # Convert Arrow table to unified records
                yield from _convert_arrow_to_unified_records(arrow_table)

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


def create_unified_estat_resource(
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
    Create a DLT resource for e-Stat API data using unified schema.

    This function creates a DLT resource that handles multiple e-Stat datasets
    with varying metadata structures by using a unified schema approach. This
    prevents PyArrow "Schema at index X was different" errors when loading
    multiple statsDataIds.

    The unified schema includes all possible fields from all datasets, with
    missing fields automatically set to None. Column order from the original
    data is preserved.

    Args:
        config: Configuration for e-Stat API source and destination
        name: Resource name (defaults to table_name from config)
        primary_key: Primary key columns (overrides config if provided)
        write_disposition: Write disposition (overrides config if provided)
        columns: Column definitions for the resource
        table_format: Table format for certain destinations
        file_format: File format for filesystem destinations
        schema_contract: Schema contract settings (defaults to evolve mode)
        table_name: Callable to generate dynamic table names
        max_table_nesting: Maximum nesting level for nested data
        selected: Whether this resource is selected for loading
        merge_key: Merge key for merge operations
        parallelized: Whether to parallelize this resource
        **resource_kwargs: Additional keyword arguments for dlt.resource

    Returns:
        dlt.Resource: Configured DLT resource with unified schema support

    Example:
        ```python
        from estat_api_dlt_helper import EstatDltConfig
        from estat_api_dlt_helper.loader.unified_schema_resource import create_unified_estat_resource

        # Configuration with multiple statsDataIds that have different schemas
        config = EstatDltConfig(
            source={
                "statsDataId": ["0004028473", "0004028474", "0004028475"],
                "app_id": "YOUR_APP_ID"
            },
            destination={
                "table_name": "unified_stats",
                "dataset_name": "estat_data"
            }
        )

        # Create resource with unified schema
        resource = create_unified_estat_resource(config)

        # Run in pipeline without schema errors
        import dlt
        pipeline = dlt.pipeline(
            pipeline_name="estat_unified",
            destination="duckdb",
            dataset_name="estat_data"
        )
        pipeline.run(resource)
        ```

    Note:
        This resource is recommended when loading multiple statsDataIds that
        may have different metadata structures (e.g., some have parent_code
        in time_metadata while others don't).
    """

    # Prepare API parameters
    from ..loader.dlt_resource import _create_api_params

    api_params = _create_api_params(config)

    # Get stats data IDs (ensure it's a list)
    stats_data_ids = config.source.statsDataId
    if isinstance(stats_data_ids, str):
        stats_data_ids = [stats_data_ids]

    # Prepare resource configuration
    resource_config: Dict[str, Any] = {
        "name": name or config.destination.table_name,
        "write_disposition": write_disposition or config.destination.write_disposition,
        "schema_contract": schema_contract
        or {
            "tables": "evolve",
            "columns": "evolve",
            "data_type": "freeze",
        },
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

    @dlt.resource(**resource_config)
    def unified_estat_data() -> Generator[Dict[str, Any], None, None]:
        """Generator function for unified e-Stat data."""
        client = EstatApiClient(app_id=config.source.app_id)

        try:
            logger.info(
                f"Processing {len(stats_data_ids)} stats data IDs with unified schema"
            )

            # Process each stats data ID
            for stats_data_id in stats_data_ids:
                yield from _fetch_unified_estat_data(
                    client=client,
                    stats_data_id=stats_data_id,
                    params=api_params,
                    limit=config.source.limit,
                    maximum_offset=config.source.maximum_offset,
                )
        finally:
            client.close()

    return unified_estat_data()
