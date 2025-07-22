# Integration Tests

This directory contains integration tests for the `estat_api_dlt_helper` package that verify the `parse_response` function works correctly with real e-Stat API data.

## Requirements

- Valid e-Stat API key set as environment variable `ESTAT_API_KEY`
- Network connectivity to access e-Stat API
- DuckDB for fetching random statistical table IDs

## Test Data Sources

The integration tests use two types of statistical table IDs:

1. **Fixed IDs** (`STATISTICAL_TABLE_IDS_FIXED`): A small set of known working statistical table IDs used for consistent testing across runs
2. **Random IDs**: Dynamically fetched from an external parquet file using DuckDB, providing broader coverage of different API response patterns

The random IDs are fetched using this SQL query:
```sql
with base as (
    select unnest(resources__resource) as resource
    from read_parquet(
        'https://data.oxon-data.work/data/estat_api/estat_data_catalog/ducklake-01980372-2c34-79b9-81c9-25f2e366840c.parquet'
    ) USING SAMPLE 10 PERCENT (bernoulli)
)
select distinct resource.URL
from base
where resource.FORMAT = 'DB'
limit 15
```

## Running Tests

### Run all integration tests
```bash
uv run pytest tests/integration -m integration -v
```

### Run specific test
```bash
uv run pytest tests/integration/test_parse_response_integration.py::TestParseResponseIntegration::test_parse_response_consistency -v
```

### Skip integration tests
```bash
uv run pytest -m "not integration"
```

## Test Coverage

The integration tests verify:
- Parser handles both fixed and random statistical table IDs from various e-Stat datasets
- Consistent parsing results for the same data
- Proper handling of different response patterns
- Graceful error handling for API failures
- Robustness across diverse statistical datasets

## Notes

- Tests will be skipped if `ESTAT_API_KEY` is not set or invalid
- Tests may be skipped if the e-Stat API is unavailable or rate-limited
- Each test fetches real data from the API, so execution time depends on network speed
- Random IDs are fetched fresh for each test run, providing ongoing coverage of new datasets
- If the external parquet file is unavailable, tests will fall back to using only the fixed IDs