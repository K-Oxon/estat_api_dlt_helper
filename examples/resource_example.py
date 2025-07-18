"""Example of using create_estat_resource individually."""

import os

import dlt

from estat_api_dlt_helper import EstatDltConfig, create_estat_resource


def main():
    """Create and use e-Stat resource manually."""
    # Configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": ["0000020203", "0000020204"],  # Multiple stats IDs
            "limit": 30,
        },
        "destination": {
            "destination": "duckdb",
            "dataset_name": "estat_resource",
            "table_name": "multi_stats",
            "write_disposition": "append",
        },
    }

    estat_config = EstatDltConfig(**config)

    # Create resource with custom parameters
    print("Creating e-Stat resource...")
    resource = create_estat_resource(
        config=estat_config,
        name="multi_stats_resource",
        write_disposition="merge",  # Override config
        primary_key=["stats_data_id", "time", "area"],  # Custom primary key
        selected=True,  # Explicitly select this resource
    )

    print(f"Resource name: {resource.name}")
    print(f"Resource write disposition: {resource.write_disposition}")
    print(f"Resource primary key: {resource.primary_key}")

    # Create a simple pipeline
    pipeline = dlt.pipeline(
        pipeline_name="resource_demo",
        destination="duckdb",
        dataset_name="estat_resource",
    )

    # Run with the resource
    print("\nRunning pipeline with resource...")
    info = pipeline.run(resource)

    print(f"\nLoad completed!")
    print(f"Tables created: {list(info.load_packages[0].schema_update.tables.keys())}")

    # Inspect the resource data generator
    print("\nInspecting resource data...")
    
    # Create a new resource instance to inspect data
    inspect_resource = create_estat_resource(
        config=estat_config,
        name="inspect_resource",
    )
    
    # Get first few records
    data_generator = inspect_resource()
    first_batch = next(data_generator)
    
    print(f"First batch schema: {first_batch.schema}")
    print(f"First batch shape: {first_batch.shape}")
    print(f"Columns: {first_batch.column_names}")
    
    # Convert to pandas for display
    df = first_batch.to_pandas()
    print(f"\nSample data (first 3 rows):")
    print(df.head(3))


if __name__ == "__main__":
    main()