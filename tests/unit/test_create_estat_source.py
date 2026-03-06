"""Tests for create_estat_source factory function."""

from estat_api_dlt_helper.config import EstatDltConfig
from estat_api_dlt_helper.loader.dlt_source import create_estat_source


STATS_DATA_ID_A = "0000020201"
STATS_DATA_ID_B = "0004028584"


def _make_config(stats_data_id, table_name, **kwargs):
    """Create a test EstatDltConfig."""
    config_kwargs = {
        "source": {
            "app_id": "test_app_id",
            "statsDataId": stats_data_id,
        },
        "destination": {
            "destination": "duckdb",
            "dataset_name": "test",
            "table_name": table_name,
            "write_disposition": "replace",
            "primary_key": None,
        },
    }
    config_kwargs.update(kwargs)
    return EstatDltConfig(**config_kwargs)


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
