"""Example of using create_estat_source to load multiple e-Stat tables at once."""

import os

import dlt

from estat_api_dlt_helper import EstatDltConfig, create_estat_source


def main():
    """Load multiple e-Stat tables using create_estat_source."""
    app_id = os.getenv("ESTAT_API_KEY", "")

    configs = [
        EstatDltConfig(
            source={
                "app_id": app_id,
                "statsDataId": "0000020201",
                "limit": 100,
                "maximum_offset": 200,
            },
            destination={
                "destination": "duckdb",
                "dataset_name": "estat_multi",
                "table_name": "population",
                "write_disposition": "merge",
                "primary_key": ["time", "area", "cat01"],
            },
        ),
        EstatDltConfig(
            source={
                "app_id": app_id,
                "statsDataId": "0000020202",
                "limit": 100,
                "maximum_offset": 200,
            },
            destination={
                "destination": "duckdb",
                "dataset_name": "estat_multi",
                "table_name": "household",
                "write_disposition": "replace",
                "primary_key": None,
            },
        ),
    ]

    source = create_estat_source(configs)

    print(f"Source name: {source.name}")
    print(f"Resources: {list(source.resources.keys())}")

    # Create pipeline and run
    pipeline = dlt.pipeline(
        pipeline_name="estat_source_demo",
        destination="duckdb",
        dataset_name="estat_multi",
    )

    print("\nRunning pipeline...")
    info = pipeline.run(source)

    print("\nLoad completed!")
    print(f"Load info: {info}")


if __name__ == "__main__":
    main()
