"""Basic example of loading e-Stat data to DuckDB using load_estat_data."""

import os

import dlt
import duckdb

from estat_api_dlt_helper import EstatDltConfig, load_estat_data


def main():
    """Load demographic statistics data to DuckDB."""
    db = duckdb.connect("estat_demo.duckdb")

    # Simple configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": "0000020201",  # 社会人口統計体系 市町村データ 人口・世帯データ
            "limit": 100,  # Small limit for demo
            "maximum_offset": 200,
        },
        "destination": {
            "pipeline_name": "estat_demo",
            "destination": dlt.destinations.duckdb(db),
            "dataset_name": "estat_api_data",
            "table_name": "population_estimates",
            "write_disposition": "replace",  # Replace existing data
        },
    }

    # Create config object
    estat_config = EstatDltConfig(**config)

    # Load data with one line
    print("Loading e-Stat data to DuckDB...")
    info = load_estat_data(estat_config)

    # Print results
    print("\nLoad completed!")
    print(f"Pipeline: {info.pipeline.pipeline_name}")
    print(f"Destination: {info.destination_name}")
    print(f"Dataset: {info.dataset_name}")

    # Access the data
    print("\nQuerying loaded data...")

    table_name = (
        f"{estat_config.destination.dataset_name}.{estat_config.destination.table_name}"
    )
    result = db.execute(f"SELECT COUNT(*) as row_count FROM {table_name}").fetchone()
    print(f"Total rows loaded: {result[0]}")

    # Show sample data
    print("\nSample data:")
    sample = db.execute(
        f"""
        SELECT *
        FROM
          {table_name} 
        LIMIT 5
        """
    ).fetchdf()
    print(sample)

    db.close()


if __name__ == "__main__":
    main()
