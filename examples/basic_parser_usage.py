"""
Basic example of using estat_api_dlt_helper parser.

This example demonstrates how to fetch data from e-Stat API
and parse it into an Arrow table.
"""

import os

import requests

from estat_api_dlt_helper import parse_response


def main():
    """Main function to demonstrate parser usage."""
    # API endpoint
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

    # Parameters for the API request
    # Note: Replace 'YOUR-API-KEY' with your actual e-Stat API key
    params = {
        "appId": os.getenv("ESTAT_API_KEY"),
        "statsDataId": "0000020201",  # 社会人口統計体系 市町村データ 人口・世帯データ
        # "cdCat01": "A2101",  # 住民基本台帳人口（日本人）
        # "cdArea": "01100,01101",  # 札幌市, 札幌市中央区
        "limit": 100,
        "maximum_offset": 200,
    }

    # Check if API key is set
    if params["appId"] is None:
        print("Error: Please set your e-Stat API key")
        print("You can set it as an environment variable:")
        print("  export ESTAT_API_KEY='your-actual-api-key'")
        print("\nTo get an API key, register at:")
        print("  https://www.e-stat.go.jp/api/")
        return

    print("Fetching data from e-Stat API...")
    print(f"Stats Data ID: {params['statsDataId']}")

    try:
        # Make API request
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        # Check for API errors
        result = data.get("GET_STATS_DATA", {}).get("RESULT", {})
        if result.get("STATUS") != 0:
            error_msg = result.get("ERROR_MSG", "Unknown error")
            print(f"API Error: {error_msg}")
            return

        # Parse the response into Arrow table
        print("\nParsing response data...")
        table = parse_response(data)

        # Display table information
        print("\n" + "=" * 60)
        print("Table Information:")
        print("=" * 60)
        print(f"Number of rows: {table.num_rows}")
        print(f"Number of columns: {table.num_columns}")

        # Display column names
        print("\nColumns:")
        for col in table.column_names:
            col_type = table.schema.field(col).type
            print(f"  - {col}: {col_type}")

        # Display data
        # Convert to pandas DataFrame
        df = table.to_pandas()
        print(df.head(5))

    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")


if __name__ == "__main__":
    main()
