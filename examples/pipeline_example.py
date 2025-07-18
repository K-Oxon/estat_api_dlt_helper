"""Example of using create_estat_pipeline individually."""

import os

from estat_api_dlt_helper import EstatDltConfig, create_estat_pipeline, create_estat_resource


def main():
    """Create and run DLT pipeline manually."""
    # Configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": "0000020202",  # 国勢調査
            "limit": 50,
        },
        "destination": {
            "destination": "duckdb",
            "dataset_name": "estat_manual",
            "table_name": "census_data",
            "write_disposition": "merge",
            "primary_key": ["time", "area"],
        },
    }

    estat_config = EstatDltConfig(**config)

    # Create pipeline with custom settings
    print("Creating DLT pipeline...")
    pipeline = create_estat_pipeline(
        config=estat_config,
        pipeline_name="custom_estat_pipeline",
        dev_mode=True,  # Enable development mode
        export_schema_path="./schemas",  # Export schemas
    )

    # Create resource
    print("Creating e-Stat resource...")
    resource = create_estat_resource(
        config=estat_config,
        name="census_resource",  # Custom resource name
    )

    # Run pipeline manually
    print("Running pipeline...")
    info = pipeline.run(
        resource,
        refresh="drop_resources",  # Drop existing resources
    )

    print(f"\nPipeline completed!")
    print(f"Pipeline name: {info.pipeline.pipeline_name}")
    print(f"Load packages: {len(info.load_packages)}")
    
    # Check pipeline state
    print(f"\nPipeline state:")
    print(f"Working directory: {pipeline.working_dir}")
    print(f"Dataset name: {pipeline.dataset_name}")
    print(f"Destination: {pipeline.destination}")
    
    # Show schema info
    schema = pipeline.default_schema
    print(f"\nSchema info:")
    print(f"Schema name: {schema.name}")
    print(f"Tables: {list(schema.tables.keys())}")


if __name__ == "__main__":
    main()