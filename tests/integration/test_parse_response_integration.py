"""Integration tests for parse_response with multiple statistical table IDs."""

import os
import re
from typing import List

import duckdb
import pyarrow as pa
import pytest

from estat_api_dlt_helper import EstatApiClient, parse_response

# List of fixed statistical table IDs that we know work well
# These are used for consistent testing across runs
STATISTICAL_TABLE_IDS_FIXED = [
    "0000020201",  # 社会人口統計体系
    "0004028584",  # GDP
]


def get_random_stat_ids(count: int = 20) -> List[str]:
    """Get random statistical table IDs from external parquet file."""
    try:
        conn = duckdb.connect()

        query = """
        with base as (
            select unnest(resources__resource) as resource
            from read_parquet(
                'https://data.oxon-data.work/data/estat_api/estat_data_catalog/ducklake-01980372-2c34-79b9-81c9-25f2e366840c.parquet'
            ) USING SAMPLE 10 PERCENT (bernoulli)
        )
        select distinct resource.URL
        from base
        where resource.FORMAT = 'DB'
        limit ?
        """

        result = conn.execute(query, [count]).fetchall()

        # Extract stats data IDs from URLs
        stat_ids = []
        for row in result:
            url_or_id = row[0]

            # First try to extract from URL parameters if it's a full URL
            match = re.search(r"statsDataId=(\d+)", url_or_id)
            if match:
                stat_ids.append(match.group(1))
            # If it's just a statistical table ID (10 digits), use it directly
            elif re.match(r"^\d{10}$", str(url_or_id)):
                stat_ids.append(str(url_or_id))

        print(f"Fetched {len(stat_ids)} random statistical table IDs from parquet file")
        return stat_ids[:count]  # Ensure we don't exceed requested count

    except Exception as e:
        # If we can't fetch from parquet, return empty list
        print(f"Warning: Could not fetch random stat IDs: {e}")
        return []


# Get API key from environment and check skip conditions
APP_ID = os.getenv("ESTAT_API_KEY")
SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION_TESTS", "").lower() == "true"

if not APP_ID or SKIP_INTEGRATION:
    skip_reason = []
    if not APP_ID:
        skip_reason.append("ESTAT_API_KEY environment variable not set")
    if SKIP_INTEGRATION:
        skip_reason.append("SKIP_INTEGRATION_TESTS is set to true")
    
    pytest.skip(" and ".join(skip_reason), allow_module_level=True)

# Combine fixed IDs with random IDs from parquet
RANDOM_STAT_IDS = get_random_stat_ids(15)  # Get 15 random IDs
STATISTICAL_TABLE_IDS = STATISTICAL_TABLE_IDS_FIXED + RANDOM_STAT_IDS

print(
    f"Integration tests will run with {len(STATISTICAL_TABLE_IDS)} statistical table IDs:"
)
print(f"  - Fixed IDs: {len(STATISTICAL_TABLE_IDS_FIXED)}")
print(f"  - Random IDs: {len(RANDOM_STAT_IDS)}")
print(f"  - Total: {len(STATISTICAL_TABLE_IDS)}")
if RANDOM_STAT_IDS:
    print(f"  - Sample random IDs: {RANDOM_STAT_IDS[:3]}...")


@pytest.mark.integration
class TestParseResponseIntegration:
    """Integration tests for parse_response with real e-Stat API data."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up API client for tests."""
        if not APP_ID:
            pytest.skip("ESTAT_API_KEY environment variable not set")
        self.client = EstatApiClient(app_id=APP_ID)

    @pytest.mark.parametrize("stats_id", STATISTICAL_TABLE_IDS)
    def test_parse_response_with_multiple_stat_ids(self, stats_id: str):
        """Test parse_response with various statistical table IDs."""
        # Fetch data from e-Stat API
        try:
            data = self.client.get_stats_data(stats_id, limit=100)
        except Exception as e:
            pytest.skip(f"Failed to fetch data for {stats_id}: {e}")

        # Check if API returned an error
        if "GET_STATS_DATA" in data:
            result = data["GET_STATS_DATA"].get("RESULT", {})
            if result.get("STATUS") != 0:
                error_msg = result.get("ERROR_MSG", "Unknown error")
                pytest.skip(f"API error for {stats_id}: {error_msg}")

            # Also check if STATISTICAL_DATA is missing
            if "STATISTICAL_DATA" not in data["GET_STATS_DATA"]:
                pytest.skip(f"No statistical data returned for {stats_id}")

        # Parse the response
        try:
            table = parse_response(data)
        except Exception as e:
            pytest.fail(f"Failed to parse response for {stats_id}: {e}")

        # Validate the result
        assert isinstance(table, pa.Table), (
            f"Result should be Arrow table for {stats_id}"
        )
        assert table.num_rows > 0, f"Table should have rows for {stats_id}"

        # Check essential columns
        assert "value" in table.column_names, f"Missing 'value' column for {stats_id}"

        # Check that we have metadata columns
        metadata_columns = [
            col for col in table.column_names if col.endswith("_metadata")
        ]
        assert len(metadata_columns) > 0, f"No metadata columns found for {stats_id}"

        # Check stat_inf column
        assert "stat_inf" in table.column_names, (
            f"Missing 'stat_inf' column for {stats_id}"
        )

        # Validate data types
        value_column = table.column("value")
        assert pa.types.is_floating(value_column.type), (
            f"Value column should be float for {stats_id}"
        )

        # Ensure non-null values exist
        values = value_column.to_pylist()
        non_null_values = [v for v in values if v is not None]
        assert len(non_null_values) > 0, f"All values are null for {stats_id}"

    def test_parse_response_consistency(self):
        """Test that parser produces consistent results for the same data."""
        stats_id = STATISTICAL_TABLE_IDS[0]

        # Fetch the same data twice
        try:
            data1 = self.client.get_stats_data(stats_id, limit=50)
            data2 = self.client.get_stats_data(stats_id, limit=50)
        except Exception as e:
            pytest.skip(f"Failed to fetch data: {e}")

        # Check for API errors in both responses
        for data in [data1, data2]:
            if "GET_STATS_DATA" in data:
                result = data["GET_STATS_DATA"].get("RESULT", {})
                if result.get("STATUS") != 0:
                    error_msg = result.get("ERROR_MSG", "Unknown error")
                    pytest.skip(f"API error: {error_msg}")
                if "STATISTICAL_DATA" not in data["GET_STATS_DATA"]:
                    pytest.skip("No statistical data returned")

        # Parse both responses
        table1 = parse_response(data1)
        table2 = parse_response(data2)

        # Check consistency
        assert table1.num_rows == table2.num_rows
        assert table1.column_names == table2.column_names

        # Check that values are the same
        values1 = table1.column("value").to_pylist()
        values2 = table2.column("value").to_pylist()
        assert values1 == values2

    def test_parse_response_different_patterns(self):
        """Test parser with different response patterns from various datasets."""
        results = []
        errors = []

        # Test a subset of IDs to check different patterns
        test_ids = STATISTICAL_TABLE_IDS[::4]  # Every 4th ID

        for stats_id in test_ids:
            try:
                data = self.client.get_stats_data(stats_id, limit=10)

                # Check for API errors
                if "GET_STATS_DATA" in data:
                    result = data["GET_STATS_DATA"].get("RESULT", {})
                    if result.get("STATUS") != 0:
                        errors.append(
                            {
                                "stats_id": stats_id,
                                "error": f"API error: {result.get('ERROR_MSG', 'Unknown error')}",
                            }
                        )
                        continue
                    if "STATISTICAL_DATA" not in data["GET_STATS_DATA"]:
                        errors.append(
                            {
                                "stats_id": stats_id,
                                "error": "No statistical data returned",
                            }
                        )
                        continue

                table = parse_response(data)

                # Collect info about successful parses
                results.append(
                    {
                        "stats_id": stats_id,
                        "num_rows": table.num_rows,
                        "num_columns": table.num_columns,
                        "column_names": table.column_names,
                    }
                )
            except Exception as e:
                errors.append(
                    {
                        "stats_id": stats_id,
                        "error": str(e),
                    }
                )

        # At least 50% should parse successfully
        success_rate = len(results) / len(test_ids)
        assert success_rate >= 0.5, (
            f"Too many parsing failures: {success_rate:.1%} success rate"
        )

        # Check that successful parses have consistent structure
        if results:
            # All should have value column
            assert all("value" in r["column_names"] for r in results)
            # All should have stat_inf column
            assert all("stat_inf" in r["column_names"] for r in results)
