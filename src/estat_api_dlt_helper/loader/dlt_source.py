"""DLT source creation for e-Stat API multi-table data."""

from typing import Any, Dict, List, Sequence

import dlt
from dlt.extract.source import DltSource

from ..config.models import EstatDltConfig
from .dlt_resource import create_estat_resource


def create_estat_source(
    configs: List[EstatDltConfig],
    **source_kwargs: Any,
) -> DltSource:
    """
    Create a DLT source for multiple e-Stat API tables.

    This function creates a DLT source containing one resource per config,
    using create_estat_resource() internally.

    Args:
        configs: List of EstatDltConfig, one per resource.
        **source_kwargs: Additional keyword arguments for dlt.source

    Returns:
        DLT source with one resource per config.

    Example:
        ```python
        from estat_api_dlt_helper import EstatDltConfig, create_estat_source

        configs = [
            EstatDltConfig(
                source={"app_id": "YOUR_KEY", "statsDataId": "0000020201"},
                destination={"destination": "duckdb", "dataset_name": "estat", "table_name": "pop"},
            ),
            EstatDltConfig(
                source={"app_id": "YOUR_KEY", "statsDataId": "0004028584"},
                destination={"destination": "duckdb", "dataset_name": "estat", "table_name": "gdp"},
            ),
        ]
        source = create_estat_source(configs)
        ```
    """
    if not configs:
        raise ValueError("configs must not be empty")

    table_names = [config.destination.table_name for config in configs]
    duplicates = [name for name in table_names if table_names.count(name) > 1]
    if duplicates:
        raise ValueError(
            f"Duplicate table names found: {sorted(set(duplicates))}"
        )

    source_config: Dict[str, Any] = dict(source_kwargs)

    @dlt.source(**source_config)
    def estat_source() -> Sequence[Any]:
        resources: List[Any] = []
        for config in configs:
            resource = create_estat_resource(config)
            resources.append(resource)
        return resources

    return estat_source()
