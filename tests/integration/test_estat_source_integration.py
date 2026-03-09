"""Integration tests for estat_source and estat_table."""

import os

import dlt
import pytest

from estat_api_dlt_helper import estat_source, estat_table

APP_ID: str = os.getenv("ESTAT_API_KEY", "")
SKIP_INTEGRATION = (
    not APP_ID or os.getenv("SKIP_INTEGRATION_TESTS", "").lower() == "true"
)


@pytest.mark.integration
@pytest.mark.skipif(
    SKIP_INTEGRATION, reason="ESTAT_API_KEY not set or SKIP_INTEGRATION_TESTS is set"
)
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
@pytest.mark.skipif(
    SKIP_INTEGRATION, reason="ESTAT_API_KEY not set or SKIP_INTEGRATION_TESTS is set"
)
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
@pytest.mark.skipif(
    SKIP_INTEGRATION, reason="ESTAT_API_KEY not set or SKIP_INTEGRATION_TESTS is set"
)
class TestEstatTableIncrementalIntegration:
    """Integration tests for estat_table with incremental loading."""

    def test_incremental_single_run(self):
        """incremental 設定でパイプラインが正常に動作することを確認."""
        pipeline = dlt.pipeline(
            pipeline_name="test_estat_table_incremental",
            destination="duckdb",
            dataset_name="test_estat_incremental_data",
        )

        resource = estat_table(
            stats_data_id="0000020201",
            app_id=APP_ID,
            table_name="pop_inc",
            write_disposition="merge",
            primary_key=["time", "area"],
            incremental=dlt.sources.incremental("time", initial_value="2020000000"),
            limit=100,
            maximum_offset=100,
        )
        info = pipeline.run(resource)
        assert info is not None


@pytest.mark.integration
@pytest.mark.skipif(
    SKIP_INTEGRATION, reason="ESTAT_API_KEY not set or SKIP_INTEGRATION_TESTS is set"
)
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
            app_id=APP_ID,
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
