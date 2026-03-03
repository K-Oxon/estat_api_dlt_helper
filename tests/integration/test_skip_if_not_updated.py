"""Integration tests for skip_if_not_updated feature."""

import uuid

import dlt
import pytest

from estat_api_dlt_helper import (
    DestinationConfig,
    EstatDltConfig,
    SourceConfig,
    create_estat_pipeline,
    create_estat_resource,
)

from .helpers import APP_ID, skip_if_no_api_key

skip_if_no_api_key()


@pytest.mark.integration
class TestSkipIfNotUpdated:
    """Integration tests for skip_if_not_updated with real e-Stat API."""

    def test_skip_on_second_run(self, tmp_path):
        """Data fetch is skipped on second run when UPDATED_DATE is unchanged."""
        # Use a unique pipeline name to avoid interference from previous test runs.
        pipeline_name = f"test_skip_{uuid.uuid4().hex[:8]}"
        pipelines_dir = str(tmp_path)

        config = EstatDltConfig(
            source=SourceConfig(
                app_id=APP_ID,
                statsDataId="0000020201",
                skip_if_not_updated=True,
                limit=10,
                maximum_offset=10,
            ),
            destination=DestinationConfig(
                destination="duckdb",
                dataset_name="test_skip",
                table_name="test_table",
                write_disposition="replace",
                primary_key=None,
                pipeline_name=pipeline_name,
            ),
        )

        # Run 1: data is fetched
        pipeline1 = create_estat_pipeline(config, pipelines_dir=pipelines_dir)
        info1 = pipeline1.run(create_estat_resource(config))

        # UPDATED_DATE should be stored in source state
        state = dlt.pipeline(
            pipeline_name=pipeline_name,
            pipelines_dir=pipelines_dir,
            destination="duckdb",
            dataset_name="test_skip",
        ).state
        source_state = state.get("sources", {})
        has_updated_dates = any(
            "updated_dates" in src_state
            for src_state in source_state.values()
        )
        assert has_updated_dates, "updated_dates not found in source_state"

        # Run 2: skipped (only empty load packages)
        pipeline2 = create_estat_pipeline(config, pipelines_dir=pipelines_dir)
        info2 = pipeline2.run(create_estat_resource(config))

        # Run 1 should contain data files, Run 2 should not
        run1_data_jobs = [
            job
            for pkg in info1.load_packages
            for job in pkg.jobs.get("completed_jobs", [])
            if job.job_file_info.table_name == "test_table"
        ]
        run2_data_jobs = [
            job
            for pkg in info2.load_packages
            for job in pkg.jobs.get("completed_jobs", [])
            if job.job_file_info.table_name == "test_table"
        ]

        assert len(run1_data_jobs) > 0, "No data loaded in Run 1"
        # Run 2 data jobs should be smaller than Run 1 (skipped)
        run1_size = sum(j.file_size for j in run1_data_jobs)
        run2_size = sum(j.file_size for j in run2_data_jobs)
        assert run2_size < run1_size, (
            f"Run 2 data size ({run2_size}) >= Run 1 ({run1_size}): skip did not work"
        )
