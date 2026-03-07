"""Tests for estat_table function."""

import inspect

import dlt
import pytest
from dlt.extract.resource import DltResource
from dlt.sources import incremental as dlt_incremental

from estat_api_dlt_helper.loader.estat_table import (
    _build_api_params,
    estat_table,
)


class TestBuildApiParams:
    """Tests for _build_api_params helper."""

    def test_filters_none_values(self):
        result = _build_api_params(lang="J", metaGetFlg="Y", cdArea=None)
        assert result == {"lang": "J", "metaGetFlg": "Y"}
        assert "cdArea" not in result

    def test_keeps_all_non_none(self):
        result = _build_api_params(lang="E", metaGetFlg="N", cdTab="001")
        assert result == {"lang": "E", "metaGetFlg": "N", "cdTab": "001"}


class TestEstatTable:
    """Tests for estat_table function."""

    def test_returns_dlt_resource(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
        )
        assert isinstance(resource, DltResource)

    def test_default_name(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
        )
        assert resource.name == "estat_0000020201"

    def test_custom_name(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
            table_name="population",
        )
        assert resource.name == "population"

    def test_default_write_disposition(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
        )
        assert resource.write_disposition == "replace"

    def test_custom_write_disposition(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
            write_disposition="merge",
        )
        assert resource.write_disposition == "merge"

    def test_primary_key(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
            write_disposition="merge",
            primary_key=["time_code", "area_code"],
        )
        schema = resource.compute_table_schema()
        pk_cols = [
            k for k, v in schema.get("columns", {}).items() if v.get("primary_key")
        ]
        assert "time_code" in pk_cols
        assert "area_code" in pk_cols

    def test_append_disposition(self):
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
            write_disposition="append",
        )
        assert resource.write_disposition == "append"

    def test_incremental_none_by_default(self):
        """incremental 未指定時は time_incremental のデフォルト値が None."""
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
        )
        sig = inspect.signature(resource._pipe.gen.__wrapped__)  # type: ignore[union-attr]
        default = sig.parameters["time_incremental"].default
        assert default is None

    def test_incremental_parameter_sets_wrapper(self):
        """incremental 指定時は time_incremental のデフォルト値に Incremental が設定される."""
        resource = estat_table(
            stats_data_id="0000020201",
            app_id="test_app_id",
            write_disposition="merge",
            primary_key=["time", "area"],
            incremental=dlt_incremental("time", initial_value="0000000000"),
        )
        sig = inspect.signature(resource._pipe.gen.__wrapped__)  # type: ignore[union-attr]
        default = sig.parameters["time_incremental"].default
        assert isinstance(default, dlt_incremental)
        assert default.cursor_path == "time"
        assert default.initial_value == "0000000000"

    def test_empty_stats_data_id_raises(self):
        with pytest.raises(ValueError, match="stats_data_id must not be empty"):
            estat_table(stats_data_id="", app_id="test_app_id")

    def test_whitespace_stats_data_id_raises(self):
        with pytest.raises(ValueError, match="stats_data_id must not be empty"):
            estat_table(stats_data_id="   ", app_id="test_app_id")

    def test_secrets_resolved_via_env(self, monkeypatch):
        """dlt.secrets.value should be resolved from environment variables."""
        monkeypatch.setenv("SOURCES__ESTAT__APP_ID", "env_secret_key")

        resource = estat_table(stats_data_id="0000020201")

        # Materialize inside a @dlt.source so dlt resolves secrets
        @dlt.source(name="estat")
        def _test_source():
            yield resource

        source = _test_source()
        # If secrets resolution failed, source creation would raise
        # ConfigFieldMissingException. Getting here means it resolved.
        assert "estat_0000020201" in source.resources
