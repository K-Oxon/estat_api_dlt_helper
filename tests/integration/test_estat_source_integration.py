"""Integration tests for estat_source and estat_table."""

import os

import dlt
import pytest

from estat_api_dlt_helper import estat_source, estat_table

APP_ID = os.getenv("ESTAT_API_KEY")
SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION_TESTS", "").lower() == "true"

if not APP_ID or SKIP_INTEGRATION:
    skip_reason = []
    if not APP_ID:
        skip_reason.append("ESTAT_API_KEY environment variable not set")
    if SKIP_INTEGRATION:
        skip_reason.append("SKIP_INTEGRATION_TESTS is set to true")

    pytest.skip(" and ".join(skip_reason), allow_module_level=True)


@pytest.mark.integration
class TestEstatSourceIntegration:
    """Integration tests for estat_source with real API."""

    def test_single_id(self):
        source = estat_source(
            stats_data_ids="0000020201",
            app_id=APP_ID,
            limit=100,
            maximum_offset=100,
        )
        assert "estat_0000020201" in source.resources

        pipeline = dlt.pipeline(
            pipeline_name="test_estat_source_single",
            destination="duckdb",
            dataset_name="test_estat_source",
        )
        info = pipeline.run(source)
        assert info is not None

    def test_multiple_ids(self):
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            app_id=APP_ID,
            limit=100,
            maximum_offset=100,
        )
        assert "estat_0000020201" in source.resources
        assert "estat_0004028584" in source.resources

        pipeline = dlt.pipeline(
            pipeline_name="test_estat_source_multi",
            destination="duckdb",
            dataset_name="test_estat_source",
        )
        info = pipeline.run(source)
        assert info is not None

    def test_custom_resource_names(self):
        source = estat_source(
            stats_data_ids={"population": "0000020201"},
            app_id=APP_ID,
            limit=100,
            maximum_offset=100,
        )
        assert "population" in source.resources

        pipeline = dlt.pipeline(
            pipeline_name="test_estat_source_custom",
            destination="duckdb",
            dataset_name="test_estat_source",
        )
        info = pipeline.run(source)
        assert info is not None


@pytest.mark.integration
class TestEstatTableIntegration:
    """Integration tests for estat_table with real API."""

    def test_standalone_resource(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id=APP_ID,
            limit=100,
            maximum_offset=100,
        )
        assert resource.name == "estat_0000020201"

        pipeline = dlt.pipeline(
            pipeline_name="test_estat_table_standalone",
            destination="duckdb",
            dataset_name="test_estat_table",
        )
        info = pipeline.run(resource)
        assert info is not None

    def test_custom_name_and_write_disposition(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id=APP_ID,
            table_name="population",
            write_disposition="replace",
            limit=100,
            maximum_offset=100,
        )
        assert resource.name == "population"
        assert resource.write_disposition == "replace"

        pipeline = dlt.pipeline(
            pipeline_name="test_estat_table_custom",
            destination="duckdb",
            dataset_name="test_estat_table",
        )
        info = pipeline.run(resource)
        assert info is not None


@pytest.mark.integration
class TestEstatSourceTablesIntegration:
    """Integration tests for estat_source with tables parameter."""

    def test_tables_parameter(self):
        source = estat_source(
            tables=[
                estat_table(
                    stats_data_id="0000020201",
                    app_id=APP_ID,
                    table_name="pop",
                    write_disposition="replace",
                    limit=100,
                    maximum_offset=100,
                ),
                estat_table(
                    stats_data_id="0004028584",
                    app_id=APP_ID,
                    table_name="gdp",
                    write_disposition="replace",
                    limit=100,
                    maximum_offset=100,
                ),
            ],
        )
        assert "pop" in source.resources
        assert "gdp" in source.resources

        pipeline = dlt.pipeline(
            pipeline_name="test_estat_source_tables",
            destination="duckdb",
            dataset_name="test_estat_source",
        )
        info = pipeline.run(source)
        assert info is not None

    def test_shared_write_disposition(self):
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            app_id=APP_ID,
            write_disposition="replace",
            limit=100,
            maximum_offset=100,
        )
        for resource in source.resources.values():
            assert resource.write_disposition == "replace"

        pipeline = dlt.pipeline(
            pipeline_name="test_estat_source_shared_wd",
            destination="duckdb",
            dataset_name="test_estat_source",
        )
        info = pipeline.run(source)
        assert info is not None
