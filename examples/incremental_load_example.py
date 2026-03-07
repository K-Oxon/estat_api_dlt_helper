"""Example of incremental loading with estat_table and estat_source."""

import os

import dlt

from estat_api_dlt_helper import estat_source, estat_table


def main():
    """Demonstrate incremental loading of e-Stat data."""
    app_id = os.getenv("ESTAT_API_KEY", "")

    # === estat_table: incremental loading ===
    # Fetch only data with time codes newer than the last loaded value.
    # On first run, loads from initial_value ("2020000000").
    # On subsequent runs, loads only new time points.

    pipeline = dlt.pipeline(
        pipeline_name="estat_incremental_demo",
        destination="duckdb",
        dataset_name="estat_incremental",
    )

    resource = estat_table(
        stats_data_id="0000020201",
        app_id=app_id,
        table_name="population",
        write_disposition="merge",
        primary_key=["time", "area"],
        incremental=dlt.sources.incremental("time", initial_value="2020000000"),
        limit=100,
        maximum_offset=200,
    )

    print("Running incremental pipeline (estat_table)...")
    info = pipeline.run(resource)
    print(f"Load info: {info}")

    # === estat_source: incremental loading across multiple tables ===
    # The same incremental config is applied to all resources.

    pipeline2 = dlt.pipeline(
        pipeline_name="estat_incremental_source_demo",
        destination="duckdb",
        dataset_name="estat_incremental_source",
    )

    source = estat_source(
        stats_data_ids=["0000020201", "0004028584"],
        app_id=app_id,
        write_disposition="merge",
        primary_key=["time", "area"],
        incremental=dlt.sources.incremental("time", initial_value="2020000000"),
        limit=100,
        maximum_offset=200,
    )

    print("\nRunning incremental pipeline (estat_source)...")
    info2 = pipeline2.run(source)
    print(f"Load info: {info2}")


if __name__ == "__main__":
    main()
