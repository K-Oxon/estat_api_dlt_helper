"""Tests for create_estat_source factory function."""

import pytest

from estat_api_dlt_helper.config import EstatDltConfig
from estat_api_dlt_helper.config.models import DestinationConfig, SourceConfig
from estat_api_dlt_helper.loader.dlt_source import create_estat_source


STATS_DATA_ID_A = "0000020201"
STATS_DATA_ID_B = "0004028584"


def _make_config(stats_data_id: str, table_name: str) -> EstatDltConfig:
    """Create a test EstatDltConfig."""
    return EstatDltConfig(
        source=SourceConfig(
            app_id="test_app_id",
            statsDataId=stats_data_id,
        ),
        destination=DestinationConfig(
            destination="duckdb",
            dataset_name="test",
            table_name=table_name,
            write_disposition="replace",
            primary_key=None,
        ),
    )


class TestCreateEstatSource:
    """Tests for create_estat_source."""

    def test_returns_dlt_source(self):
        """Returns a DltSource object with resources and name."""
        configs = [_make_config(STATS_DATA_ID_A, "population")]
        source = create_estat_source(configs)
        assert hasattr(source, "resources")
        assert hasattr(source, "name")

    def test_resource_names(self):
        """Each config's table_name becomes a resource name."""
        configs = [
            _make_config(STATS_DATA_ID_A, "population"),
            _make_config(STATS_DATA_ID_B, "household"),
        ]
        source = create_estat_source(configs)
        assert "population" in source.resources
        assert "household" in source.resources

    def test_resource_count(self):
        """Number of resources matches number of configs."""
        configs = [
            _make_config(STATS_DATA_ID_A, "population"),
            _make_config(STATS_DATA_ID_B, "household"),
        ]
        source = create_estat_source(configs)
        assert len(source.resources) == 2

    def test_single_config(self):
        """Works with a single config."""
        configs = [_make_config(STATS_DATA_ID_A, "t1")]
        source = create_estat_source(configs)
        assert "t1" in source.resources
        assert len(source.resources) == 1

    def test_empty_configs_raises(self):
        """Empty configs list raises ValueError."""
        with pytest.raises(ValueError, match="configs must not be empty"):
            create_estat_source([])

    def test_duplicate_table_names_raises(self):
        """Duplicate table names raise ValueError."""
        configs = [
            _make_config(STATS_DATA_ID_A, "same_name"),
            _make_config(STATS_DATA_ID_B, "same_name"),
        ]
        with pytest.raises(ValueError, match="Duplicate table names"):
            create_estat_source(configs)
