"""Basic example of loading e-Stat data to DuckDB using load_estat_data."""

import os

import dlt

from estat_api_dlt_helper import EstatDltConfig, load_estat_data

dlt.config["destination.bigquery.project_id"] = "YOUR_PROJECT_ID"
dlt.config["destination.bigquery.location"] = "asia-northeast1"
dlt.config["destination.bigquery.autodetect_schema"] = True


def main():
    """Load demographic statistics data to BigQuery."""

    # Simple configuration
    config = {
        "source": {
            "app_id": os.getenv("ESTAT_API_KEY"),
            "statsDataId": "0000020201",  # 社会人口統計体系
            "limit": 100,  # 1 requestで取得する行数 | デフォルト:10万
            "maximum_offset": 200,  # 最大取得行数
        },
        "destination": {
            "pipeline_name": "estat_demo",
            "destination": "bigquery",
            "dataset_name": "estat_api_data",
            "table_name": "population_estimates",
            "write_disposition": "replace",  # Replace existing data
            "dev_mode": True,
        },
    }

    # Create config object
    estat_config = EstatDltConfig(**config)  # type: ignore

    # Load data with one line
    print("Loading e-Stat data to BigQuery...")
    info = load_estat_data(estat_config)

    # Print results
    print("\nLoad completed!")
    print(info)


if __name__ == "__main__":
    main()
