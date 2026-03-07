"""DLT source for e-Stat API data."""

from typing import Any, Dict, Iterable, List, Optional, Union

import dlt
from dlt.extract.resource import DltResource
from dlt.sources import incremental as dlt_incremental

from .estat_table import estat_table


def _normalize_stats_data_ids(
    stats_data_ids: Union[str, List[str], Dict[str, str]],
) -> Dict[str, str]:
    """Normalize stats_data_ids to Dict[resource_name, stats_data_id].

    Args:
        stats_data_ids: Statistical table ID(s) in one of three formats:
            - str: single ID
            - List[str]: multiple IDs
            - Dict[str, str]: {resource_name: stats_data_id} mapping

    Returns:
        Dict mapping resource_name to stats_data_id.
    """
    if isinstance(stats_data_ids, str):
        return {f"estat_{stats_data_ids}": stats_data_ids}
    if not stats_data_ids:
        raise ValueError("stats_data_ids must not be empty")
    if isinstance(stats_data_ids, list):
        seen: set[str] = set()
        duplicates: set[str] = set()
        for sid in stats_data_ids:
            if sid in seen:
                duplicates.add(sid)
            else:
                seen.add(sid)
        if duplicates:
            dup_list = ", ".join(sorted(duplicates))
            raise ValueError(
                f"Duplicate stats_data_ids detected in list input: {dup_list}"
            )
        return {f"estat_{sid}": sid for sid in stats_data_ids}
    return stats_data_ids


@dlt.source(name="estat")
def estat_source(
    stats_data_ids: Union[str, List[str], Dict[str, str], None] = None,
    tables: Optional[List[DltResource]] = None,
    app_id: str = dlt.secrets.value,
    write_disposition: str = "replace",
    primary_key: Optional[Union[str, List[str]]] = None,
    incremental: Optional[dlt_incremental[str]] = None,
    limit: int = 100000,
    maximum_offset: Optional[int] = None,
    timeout: int = 60,
    **api_params: Any,
) -> Iterable[DltResource]:
    """Create a DLT source for e-Stat API statistical data.

    Supports two modes:
    - stats_data_ids: Each ID becomes a separate DLT resource via estat_table,
      sharing write_disposition/primary_key settings.
    - tables: Pass pre-configured estat_table resources directly for
      per-resource control.

    Args:
        stats_data_ids: Statistical table ID(s) to fetch. Accepts:
            - str: single ID (resource name: "estat_{id}")
            - List[str]: multiple IDs (resource names: "estat_{id}")
            - Dict[str, str]: {resource_name: stats_data_id} for custom names
        tables: Pre-configured DltResource list (from estat_table).
            When provided, write_disposition/primary_key/app_id are ignored
            as each resource carries its own settings.
        app_id: e-Stat API application ID. Resolved automatically from
            secrets.toml ([sources.estat] app_id) or environment variable
            (SOURCES__ESTAT__APP_ID) if not provided.
        write_disposition: How to write data to destination.
            Applied to all resources when using stats_data_ids.
        primary_key: Primary key column(s) for merge disposition.
            Applied to all resources when using stats_data_ids.
        incremental: Optional incremental loading configuration.
            Applied to all resources when using stats_data_ids mode.
            Ignored when using tables mode (each table carries its own config).
        limit: Maximum records per API request (pagination size).
        maximum_offset: Maximum total records to fetch. None for unlimited.
        timeout: API request timeout in seconds.
        **api_params: Additional e-Stat API parameters passed directly to the
            API request (e.g., lang, lvTab, cdTab, cdTime, cdArea, cdTimeFrom,
            cdTimeTo, metaGetFlg, cntGetFlg, replaceSpChars, cat01, etc.).

    Returns:
        DLT source with one resource per stats_data_id.

    Raises:
        ValueError: If both stats_data_ids and tables are provided,
            if neither is provided, or if tables is an empty list.

    Example:
        ```python
        import dlt
        from estat_api_dlt_helper import estat_source, estat_table

        # Simple: multiple tables with shared settings
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            write_disposition="merge",
            primary_key=["time_code", "area_code"],
        )

        # Advanced: per-resource settings
        source = estat_source(
            tables=[
                estat_table(stats_data_id="0000020201", table_name="pop",
                            write_disposition="merge", primary_key=["time_code"]),
                estat_table(stats_data_id="0004028584", table_name="gdp",
                            write_disposition="replace"),
            ],
        )

        pipeline = dlt.pipeline(
            pipeline_name="estat",
            destination="duckdb",
            dataset_name="estat_data",
        )
        pipeline.run(source)
        ```
    """
    if tables is not None and stats_data_ids is not None:
        raise ValueError(
            "Cannot specify both stats_data_ids and tables. Use one or the other."
        )
    if tables is None and stats_data_ids is None:
        raise ValueError("Either stats_data_ids or tables must be provided.")
    if tables is not None and not tables:
        raise ValueError("tables must not be empty")

    if tables is not None:
        yield from tables
        return

    assert stats_data_ids is not None  # guaranteed by validation above
    id_map = _normalize_stats_data_ids(stats_data_ids)
    for resource_name, stats_data_id in id_map.items():
        yield estat_table(
            stats_data_id=stats_data_id,
            app_id=app_id,
            table_name=resource_name,
            write_disposition=write_disposition,
            primary_key=primary_key,
            incremental=incremental,
            limit=limit,
            maximum_offset=maximum_offset,
            timeout=timeout,
            **api_params,
        )
