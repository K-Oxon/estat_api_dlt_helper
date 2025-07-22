"""
Demo script showing how to use the EstatApiClient.

This script demonstrates basic usage of the e-Stat API client.
To run with actual API access, you need to set ESTAT_API_KEY environment variable.
"""

import os

from estat_api_dlt_helper.api.client import EstatApiClient


def demo_api_client():
    """Demonstrate API client usage"""
    # Get API key from environment
    api_key = os.getenv("ESTAT_API_KEY")

    if not api_key:
        print(
            "Warning: ESTAT_API_KEY not set. This demo will show usage but not make actual API calls."
        )
        print("\nTo test with real API:")
        print("1. Get API key from https://www.e-stat.go.jp/api/")
        print("2. Set environment variable: export ESTAT_API_KEY=your_key_here")
        print("3. Run this script again")
        return

    # Initialize client
    client = EstatApiClient(app_id=api_key)

    try:
        print("Testing e-Stat API client...")

        # Test with a sample statistics data ID
        # This is a real statistics ID for population census data
        stats_data_id = "0000020202"

        print(f"Fetching data for statsDataId: {stats_data_id}")
        print("Requesting first 10 records...")

        # Get small sample of data
        response = client.get_stats_data(
            stats_data_id=stats_data_id, limit=10, start_position=1
        )

        # Display response structure
        print("\nAPI Response Structure:")
        if "GET_STATS_DATA" in response:
            stats_data = response["GET_STATS_DATA"]
            if "STATISTICAL_DATA" in stats_data:
                statistical_data = stats_data["STATISTICAL_DATA"]

                # Show result info
                if "RESULT_INF" in statistical_data:
                    result_inf = statistical_data["RESULT_INF"]
                    print(f"Total records: {result_inf.get('TOTAL_NUMBER', 'N/A')}")
                    print(
                        f"Retrieved: {result_inf.get('FROM_NUMBER', 'N/A')}-{result_inf.get('TO_NUMBER', 'N/A')}"
                    )

                # Show table structure
                if "TABLE_INF" in statistical_data:
                    table_inf = statistical_data["TABLE_INF"]
                    if "VALUE" in table_inf and table_inf["VALUE"]:
                        print(f"Sample data records: {len(table_inf['VALUE'])}")
                        print(
                            "First record keys:",
                            list(table_inf["VALUE"][0].keys())
                            if table_inf["VALUE"]
                            else "No data",
                        )

                # Show metadata structure
                if "CLASS_INF" in statistical_data:
                    class_inf = statistical_data["CLASS_INF"]
                    print(f"Metadata classes: {len(class_inf.get('CLASS_OBJ', []))}")

        print("\n✅ API client test successful!")

    except Exception as e:
        print(f"\n❌ API client test failed: {e}")

    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    demo_api_client()
