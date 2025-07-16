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
        "appId": os.getenv("ESTAT_API_KEY", "YOUR-API-KEY"),
        "statsDataId": "0000020201",  # 市区町村データ 基礎データ
        "cdCat01": "A2101",           # 住民基本台帳人口（日本人）
        "cdArea": "01100,01101",      # 札幌市, 札幌市中央区
        "limit": 10
    }
    
    # Check if API key is set
    if params["appId"] == "YOUR-API-KEY":
        print("Error: Please set your e-Stat API key")
        print("You can set it as an environment variable:")
        print("  export ESTAT_API_KEY='your-actual-api-key'")
        print("\nTo get an API key, register at:")
        print("  https://www.e-stat.go.jp/api/")
        return
    
    print("Fetching data from e-Stat API...")
    print(f"Stats Data ID: {params['statsDataId']}")
    print(f"Category: {params['cdCat01']}")
    print(f"Areas: {params['cdArea']}")
    
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
        print("\n" + "=" * 60)
        print("Data:")
        print("=" * 60)
        
        for i in range(min(5, table.num_rows)):
            print(f"\n--- Row {i + 1} ---")
            
            # Basic fields
            print(f"Area: {table['area'][i].as_py()}")
            print(f"Time: {table['time'][i].as_py()}")
            print(f"Value: {table['value'][i].as_py():,.0f}")
            
            # Area metadata
            area_metadata = table['area_metadata'][i].as_py()
            print(f"Area Name: {area_metadata['name']}")
            print(f"Area Level: {area_metadata['level']}")
            
            if area_metadata.get('parent_code'):
                print(f"Parent Code: {area_metadata['parent_code']}")
        
        # Summary
        print("\n" + "=" * 60)
        print("Summary:")
        print("=" * 60)
        
        # Get unique areas
        unique_areas = set()
        for i in range(table.num_rows):
            metadata = table['area_metadata'][i].as_py()
            unique_areas.add(metadata['name'])
        
        print(f"Number of unique areas: {len(unique_areas)}")
        print("Areas:")
        for area in sorted(unique_areas):
            print(f"  - {area}")
        
        # Calculate total
        total = sum(table['value'][i].as_py() for i in range(table.num_rows))
        print(f"\nTotal value: {total:,.0f}")
        
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")


if __name__ == "__main__":
    main()