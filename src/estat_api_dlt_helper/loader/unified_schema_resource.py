"""DLT resource with unified schema for handling different metadata structures."""

from typing import Any, Callable, Dict, Generator, List, Optional

import dlt
import pyarrow as pa
from pydantic import ValidationError

from ..api.client import EstatApiClient
from ..config.models import EstatDltConfig
from ..models import ClassInfModel, TableInf
from ..models.unified_schema import (
    UnifiedAreaMetadata,
    UnifiedCategoryMetadata,
    UnifiedEstatRecord,
    UnifiedStatInf,
    UnifiedTabMetadata,
    UnifiedTimeMetadata,
)
from ..utils import create_arrow_struct_type, model_to_arrow_dict
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
) -> Generator[UnifiedEstatRecord, None, None]:
    """Convert Arrow table to unified records."""

    # Import pandas here to avoid global import issues
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for unified schema conversion")

    # Convert to pandas for easier processing
    df = arrow_table.to_pandas()

    for _, row in df.iterrows():
        record_data = {}
        extra_dimensions = {}
        extra_metadata = {}

        # Process each column
        for col_name in df.columns:
            value = row[col_name]

            # Handle None/NaN values
            if pd.isna(value):
                value = None

            if col_name == "stat_inf":
                # Convert stat_inf to UnifiedStatInf
                if value is not None:
                    try:
                        record_data["stat_inf"] = UnifiedStatInf(**value)
                    except (ValidationError, TypeError) as e:
                        logger.warning(f"Failed to convert stat_inf: {e}")
                        continue
            elif col_name.endswith("_metadata"):
                # Handle metadata columns
                field_name = col_name.replace("_metadata", "")
                if value is not None and isinstance(value, dict):
                    unified_metadata = _convert_to_unified_metadata(field_name, value)
                    if unified_metadata is not None:
                        record_data[col_name] = unified_metadata
                    else:
                        extra_metadata[col_name] = value
                else:
                    extra_metadata[col_name] = value
            elif col_name in UnifiedEstatRecord.model_fields:
                # Handle known fields
                record_data[col_name] = value
            else:
                # Handle unknown dimension columns
                if not col_name.endswith("_metadata"):
                    extra_dimensions[col_name] = value
                else:
                    extra_metadata[col_name] = value

        # Add extra fields if any
        if extra_dimensions:
            record_data["extra_dimensions"] = extra_dimensions
        if extra_metadata:
            record_data["extra_metadata"] = extra_metadata

        try:
            yield UnifiedEstatRecord(**record_data)
        except ValidationError as e:
            logger.warning(f"Failed to create unified record: {e}")
            continue


def _fetch_unified_estat_data(
    client: EstatApiClient,
    stats_data_id: str,
    params: Dict[str, Any],
    limit: int = 100000,
    maximum_offset: Optional[int] = None,
) -> Generator[UnifiedEstatRecord, None, None]:
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

    This resource uses a unified Pydantic schema that can handle all possible
    metadata structures, preventing schema mismatch errors.
    """
    # pandas will be imported locally in the conversion function

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
    def unified_estat_data() -> Generator[UnifiedEstatRecord, None, None]:
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
