"""DLT resource for a single e-Stat statistical table."""

from typing import Any, Dict, Generator, List, Optional, Union

import dlt
import pyarrow as pa
from dlt.extract.resource import DltResource

from ..api.client import EstatApiClient
from .dlt_resource import _fetch_estat_data


_DEFAULT_API_PARAMS: Dict[str, str] = {
    "lang": "J",
    "metaGetFlg": "Y",
    "cntGetFlg": "N",
    "explanationGetFlg": "Y",
    "annotationGetFlg": "Y",
    "replaceSpChars": "2",
}


def _build_api_params(**params: Any) -> Dict[str, Any]:
    """Build API parameters dictionary, filtering out None values."""
    return {k: v for k, v in params.items() if v is not None}


def estat_table(
    stats_data_id: str,
    app_id: str = dlt.secrets.value,
    table_name: Optional[str] = None,
    write_disposition: str = "replace",
    primary_key: Optional[Union[str, List[str]]] = None,
    limit: int = 100000,
    maximum_offset: Optional[int] = None,
    timeout: int = 60,
    **api_params: Any,
) -> DltResource:
    """Create a DLT resource for a single e-Stat statistical table.

    Use this function directly when you need fine-grained control over
    write_disposition and primary_key per resource.

    Args:
        stats_data_id: Statistical table ID to fetch.
        app_id: e-Stat API application ID. Resolved automatically from
            secrets.toml or environment variables when used inside a
            @dlt.source or @dlt.resource context.
        table_name: Resource/table name. Defaults to "estat_{stats_data_id}".
        write_disposition: How to write data to destination.
        primary_key: Primary key column(s) for merge disposition.
        limit: Maximum records per API request (pagination size).
        maximum_offset: Maximum total records to fetch. None for unlimited.
        timeout: API request timeout in seconds.
        **api_params: Additional e-Stat API parameters (e.g., lang, cdTab,
            cdArea, cdTime, cdTimeFrom, cdTimeTo, cat01, etc.).

    Returns:
        DLT resource yielding PyArrow tables.

    Example:
        ```python
        import dlt
        from estat_api_dlt_helper import estat_table

        resource = estat_table(
            stats_data_id="0000020201",
            write_disposition="merge",
            primary_key=["time_code", "area_code"],
        )
        pipeline = dlt.pipeline(
            pipeline_name="estat",
            destination="duckdb",
            dataset_name="estat_data",
        )
        pipeline.run(resource)
        ```
    """
    resource_name = table_name or f"estat_{stats_data_id}"

    merged_params = {**_DEFAULT_API_PARAMS, **api_params}
    params = _build_api_params(**merged_params)

    @dlt.resource(
        name=resource_name,
        write_disposition=write_disposition,
        primary_key=primary_key,
        schema_contract={
            "tables": "evolve",
            "columns": "evolve",
            "data_type": "freeze",
        },
    )
    def _estat_data(
        app_id: str = app_id,
    ) -> Generator[pa.Table, None, None]:
        client = EstatApiClient(app_id=app_id, timeout=timeout)
        try:
            yield from _fetch_estat_data(
                client=client,
                stats_data_id=stats_data_id,
                params=params,
                limit=limit,
                maximum_offset=maximum_offset,
            )
        finally:
            client.close()

    return _estat_data
