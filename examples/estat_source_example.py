"""Example of using estat_source and estat_table to load e-Stat data with dlt."""

import os

import dlt

from estat_api_dlt_helper import estat_source, estat_table


def main():
    """Load e-Stat data using estat_source and estat_table."""
    app_id = os.getenv("ESTAT_API_KEY", "")

    # === estat_source: multiple tables at once ===

    source = estat_source(
        stats_data_ids=["0000020201", "0004028584"],
        app_id=app_id,
        limit=100,
        maximum_offset=200,
    )

    print(f"Source name: {source.name}")
    print(f"Resources: {list(source.resources.keys())}")

    pipeline = dlt.pipeline(
        pipeline_name="estat_source_demo",
        destination="duckdb",
        dataset_name="estat_data",
    )

    print("\nRunning pipeline...")
    info = pipeline.run(source)
    print(f"Load info: {info}")

    # === estat_source: shared write_disposition / primary_key ===

    source = estat_source(
        stats_data_ids={"population": "0000020201", "gdp": "0004028584"},
        app_id=app_id,
        write_disposition="merge",
        primary_key=["time_code", "area_code"],
        limit=100,
        maximum_offset=200,
    )

    print(f"\nCustom resource names: {list(source.resources.keys())}")

    pipeline2 = dlt.pipeline(
        pipeline_name="estat_source_custom",
        destination="duckdb",
        dataset_name="estat_custom",
    )

    info2 = pipeline2.run(source)
    print(f"Load info: {info2}")

    # === estat_source: per-resource settings via tables parameter ===

    source = estat_source(
        tables=[
            estat_table(
                stats_data_id="0000020201",
                app_id=app_id,
                table_name="pop",
                write_disposition="merge",
                primary_key=["time_code"],
                limit=100,
                maximum_offset=200,
            ),
            estat_table(
                stats_data_id="0004028584",
                app_id=app_id,
                table_name="gdp",
                write_disposition="replace",
                limit=100,
                maximum_offset=200,
            ),
        ],
    )

    print(f"\nTables parameter: {list(source.resources.keys())}")

    pipeline3 = dlt.pipeline(
        pipeline_name="estat_source_tables",
        destination="duckdb",
        dataset_name="estat_tables",
    )

    info3 = pipeline3.run(source)
    print(f"Load info: {info3}")

    # === estat_table: single table with fine-grained control ===

    resource = estat_table(
        stats_data_id="0000020201",
        app_id=app_id,
        table_name="population",
        write_disposition="replace",
        limit=100,
        maximum_offset=200,
    )

    print(f"\nResource name: {resource.name}")
    print(f"Write disposition: {resource.write_disposition}")

    pipeline4 = dlt.pipeline(
        pipeline_name="estat_table_demo",
        destination="duckdb",
        dataset_name="estat_table_data",
    )

    info4 = pipeline4.run(resource)
    print(f"Load info: {info4}")


if __name__ == "__main__":
    main()
