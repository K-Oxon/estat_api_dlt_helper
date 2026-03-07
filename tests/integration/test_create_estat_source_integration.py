"""Integration tests for create_estat_source."""

import os

import dlt
import pytest

from estat_api_dlt_helper import EstatDltConfig, create_estat_source


def _make_config(stats_data_id, table_name):
    """Create a test EstatDltConfig."""
    return EstatDltConfig(
        source={
            "app_id": os.getenv("ESTAT_API_KEY", ""),
            "statsDataId": stats_data_id,
            "limit": 100,
            "maximum_offset": 100,
        },
        destination={
            "destination": "duckdb",
            "dataset_name": "test_create_source",
            "table_name": table_name,
            "write_disposition": "replace",
            "primary_key": None,
        },
    )


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ESTAT_API_KEY") or os.getenv("SKIP_INTEGRATION_TESTS", "").lower() == "true",
    reason="ESTAT_API_KEY not set or SKIP_INTEGRATION_TESTS is set",
)
class TestCreateEstatSourceIntegration:
    """Integration tests for create_estat_source with real API."""

    def test_single_config(self):
        """Single config loads successfully."""
        configs = [_make_config("0000020201", "population")]
        source = create_estat_source(configs)
        assert "population" in source.resources

        pipeline = dlt.pipeline(
            pipeline_name="test_create_source_single",
            destination="duckdb",
            dataset_name="test_create_source",
        )
        info = pipeline.run(source)
        assert info is not None

    def test_multiple_configs(self):
        """Multiple configs load all resources."""
        configs = [
            _make_config("0000020201", "table_a"),
            _make_config("0004028584", "table_b"),
        ]
        source = create_estat_source(configs)
        assert "table_a" in source.resources
        assert "table_b" in source.resources

        pipeline = dlt.pipeline(
            pipeline_name="test_create_source_multi",
            destination="duckdb",
            dataset_name="test_create_source",
        )
        info = pipeline.run(source)
        assert info is not None
