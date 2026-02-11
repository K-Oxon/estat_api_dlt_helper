"""Tests for timeout passthrough from EstatDltConfig to EstatApiClient."""

from unittest.mock import MagicMock, patch

from estat_api_dlt_helper.config import EstatDltConfig
from estat_api_dlt_helper.loader.dlt_resource import create_estat_resource
from estat_api_dlt_helper.loader.unified_schema_resource import (
    create_unified_estat_resource,
)

STATS_DATA_ID = "0004040081"


def _make_config(timeout=None):
    """Create a test EstatDltConfig with optional timeout."""
    kwargs = {
        "source": {
            "app_id": "test_app_id",
            "statsDataId": STATS_DATA_ID,
        },
        "destination": {
            "destination": "duckdb",
            "dataset_name": "test",
            "table_name": "test_table",
            "write_disposition": "replace",
            "primary_key": None,
        },
    }
    if timeout is not None:
        kwargs["timeout"] = timeout
    return EstatDltConfig(**kwargs)


class TestCreateEstatResourceTimeout:
    """Test that create_estat_resource passes timeout to EstatApiClient."""

    @patch("estat_api_dlt_helper.loader.dlt_resource.EstatApiClient")
    def test_timeout_specified(self, mock_client_cls: MagicMock):
        """timeout を指定した場合、EstatApiClient に渡されること。"""
        mock_client = MagicMock()
        mock_client.get_stats_data_generator.return_value = iter([])
        mock_client_cls.return_value = mock_client

        config = _make_config(timeout=120)
        resource = create_estat_resource(config)

        # Consume the generator to trigger client creation
        list(resource)

        mock_client_cls.assert_called_once_with(app_id="test_app_id", timeout=120)

    @patch("estat_api_dlt_helper.loader.dlt_resource.EstatApiClient")
    def test_timeout_not_specified(self, mock_client_cls: MagicMock):
        """timeout 未指定時はデフォルト(60秒)が使われること。"""
        mock_client = MagicMock()
        mock_client.get_stats_data_generator.return_value = iter([])
        mock_client_cls.return_value = mock_client

        config = _make_config(timeout=None)
        resource = create_estat_resource(config)

        list(resource)

        # timeout kwarg should NOT be passed, letting the default (60) apply
        mock_client_cls.assert_called_once_with(app_id="test_app_id")


class TestCreateUnifiedEstatResourceTimeout:
    """Test that create_unified_estat_resource passes timeout to EstatApiClient."""

    @patch("estat_api_dlt_helper.loader.unified_schema_resource.EstatApiClient")
    def test_timeout_specified(self, mock_client_cls: MagicMock):
        """timeout を指定した場合、EstatApiClient に渡されること。"""
        mock_client = MagicMock()
        mock_client.get_stats_data_generator.return_value = iter([])
        mock_client_cls.return_value = mock_client

        config = _make_config(timeout=120)
        resource = create_unified_estat_resource(config)

        list(resource)

        mock_client_cls.assert_called_once_with(app_id="test_app_id", timeout=120)

    @patch("estat_api_dlt_helper.loader.unified_schema_resource.EstatApiClient")
    def test_timeout_not_specified(self, mock_client_cls: MagicMock):
        """timeout 未指定時はデフォルト(60秒)が使われること。"""
        mock_client = MagicMock()
        mock_client.get_stats_data_generator.return_value = iter([])
        mock_client_cls.return_value = mock_client

        config = _make_config(timeout=None)
        resource = create_unified_estat_resource(config)

        list(resource)

        mock_client_cls.assert_called_once_with(app_id="test_app_id")
