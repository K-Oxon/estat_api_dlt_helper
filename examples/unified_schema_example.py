"""Example: Using unified schema to handle multiple stats IDs with different schemas."""

import os

import dlt
import duckdb

from estat_api_dlt_helper import (
    EstatDltConfig,
    create_estat_pipeline,
    create_unified_estat_resource,
)


def main():
    """Demonstrate unified schema approach for multiple stats IDs."""
    db = duckdb.connect("estat_demo_2.duckdb")

    # Configuration for multiple stats IDs with potentially different schemas
    config = EstatDltConfig(
        source={
            "app_id": os.getenv("ESTAT_API_KEY", "your_app_id_here"),
            "statsDataId": [
                "0004028473",
                "0004028474",
                "0004028475",
                "0004028476",
                "0004028477",
                "0004028478",
                "0004028479",
                "0004028480",
                "0004028481",
                "0004028482",
                "0004028483",
                "0004028484",
                "0004028485",
            ],
            "limit": 100,  # Limit per request for testing
            "maximum_offset": 200,  # Total limit for testing
        },
        destination={
            "pipeline_name": "unified_stats_data",
            "destination": dlt.destinations.duckdb(db),
            "dataset_name": "estat_api_data",
            "table_name": "unified_stats_data",
            "write_disposition": "replace",
        },
    )

    # Create DLT pipeline
    pipeline = create_estat_pipeline(
        config=config,
        pipeline_name="estat_unified_schema_pipeline",
    )

    # Create unified schema resource
    resource = create_unified_estat_resource(config)

    print(f"Loading {len(config.source.statsDataId)} stats IDs with unified schema...")
    print("This approach uses Pydantic models to define a unified schema")
    print("that can handle all possible metadata variations.\n")

    try:
        # Run the pipeline
        load_info = pipeline.run(resource)

        print("\n" + "=" * 60)
        print("✅ LOAD COMPLETED SUCCESSFULLY WITH UNIFIED SCHEMA!")
        print("=" * 60)

        # Print load info
        print(load_info)

        # Query loaded data to verify unified schema
        # Check total row count
        result = db.execute(
            f"SELECT COUNT(*) as total_rows FROM {config.destination.table_name}"
        ).fetchone()
        print(f"Total rows loaded: {result[0]}")
        db.close()

    except Exception as e:
        print(f"\n❌ Error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        raise


if __name__ == "__main__":
    main()
