"""Tests for estat_source function."""

import inspect

import dlt
import pytest
from dlt.extract.source import DltSource

from estat_api_dlt_helper.loader.estat_source import (
    _normalize_stats_data_ids,
    estat_source,
)
from estat_api_dlt_helper.loader.estat_table import estat_table


class TestNormalizeStatsDataIds:
    """Tests for _normalize_stats_data_ids helper."""

    def test_single_string(self):
        result = _normalize_stats_data_ids("0000020201")
        assert result == {"estat_0000020201": "0000020201"}

    def test_list_of_strings(self):
        result = _normalize_stats_data_ids(["0000020201", "0004028584"])
        assert result == {
            "estat_0000020201": "0000020201",
            "estat_0004028584": "0004028584",
        }

    def test_dict_mapping(self):
        result = _normalize_stats_data_ids(
            {"population": "0000020201", "gdp": "0004028584"}
        )
        assert result == {"population": "0000020201", "gdp": "0004028584"}

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            _normalize_stats_data_ids([])

    def test_empty_dict_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            _normalize_stats_data_ids({})

    def test_single_item_list(self):
        result = _normalize_stats_data_ids(["0000020201"])
        assert result == {"estat_0000020201": "0000020201"}

    def test_duplicate_ids_raises(self):
        with pytest.raises(ValueError, match="Duplicate stats_data_ids detected"):
            _normalize_stats_data_ids(["0000020201", "0004028584", "0000020201"])


class TestEstatSource:
    """Tests for estat_source function."""

    def test_returns_source_with_single_id(self):
        source = estat_source(
            stats_data_ids="0000020201",
            app_id="test_app_id",
        )
        assert isinstance(source, DltSource)

    def test_returns_source_with_list(self):
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            app_id="test_app_id",
        )
        assert isinstance(source, DltSource)

    def test_returns_source_with_dict(self):
        source = estat_source(
            stats_data_ids={"population": "0000020201"},
            app_id="test_app_id",
        )
        assert isinstance(source, DltSource)

    def test_resource_names_from_string(self):
        source = estat_source(
            stats_data_ids="0000020201",
            app_id="test_app_id",
        )
        assert "estat_0000020201" in source.resources

    def test_resource_names_from_list(self):
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            app_id="test_app_id",
        )
        assert "estat_0000020201" in source.resources
        assert "estat_0004028584" in source.resources

    def test_resource_names_from_dict(self):
        source = estat_source(
            stats_data_ids={"population": "0000020201", "gdp": "0004028584"},
            app_id="test_app_id",
        )
        assert "population" in source.resources
        assert "gdp" in source.resources

    def test_resource_count_matches_ids(self):
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            app_id="test_app_id",
        )
        assert len(source.resources) == 2

    def test_single_id_has_one_resource(self):
        source = estat_source(
            stats_data_ids="0000020201",
            app_id="test_app_id",
        )
        assert len(source.resources) == 1

    def test_source_name(self):
        source = estat_source(
            stats_data_ids="0000020201",
            app_id="test_app_id",
        )
        assert source.name == "estat"

    def test_write_disposition_applied_to_all_resources(self):
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            app_id="test_app_id",
            write_disposition="merge",
        )
        for resource in source.resources.values():
            assert resource.write_disposition == "merge"

    def test_primary_key_applied_to_all_resources(self):
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            app_id="test_app_id",
            write_disposition="merge",
            primary_key=["time_code", "area_code"],
        )
        for resource in source.resources.values():
            schema = resource.compute_table_schema()
            pk_cols = [
                k for k, v in schema.get("columns", {}).items() if v.get("primary_key")
            ]
            assert "time_code" in pk_cols
            assert "area_code" in pk_cols

    def test_tables_parameter(self):
        source = estat_source(
            tables=[
                estat_table(
                    stats_data_id="0000020201",
                    app_id="test_app_id",
                    table_name="pop",
                    write_disposition="merge",
                    primary_key=["time_code"],
                ),
                estat_table(
                    stats_data_id="0004028584",
                    app_id="test_app_id",
                    table_name="gdp",
                    write_disposition="replace",
                ),
            ],
            app_id="unused",
        )
        assert "pop" in source.resources
        assert "gdp" in source.resources
        assert source.resources["pop"].write_disposition == "merge"
        assert source.resources["gdp"].write_disposition == "replace"

    def test_tables_app_id_propagated_from_source(self):
        """tables モードで source の app_id が各 table の app_id を上書きする."""
        source = estat_source(
            tables=[
                estat_table(
                    stats_data_id="0000020201",
                    app_id="placeholder",
                    table_name="pop",
                ),
                estat_table(
                    stats_data_id="0004028584",
                    app_id="placeholder",
                    table_name="gdp",
                ),
            ],
            app_id="source_app_id",
        )
        for resource in source.resources.values():
            assert resource.explicit_args.get("app_id") == "source_app_id"

    def test_tables_limit_maximum_offset_timeout_propagated_from_source(self):
        """tables モードで limit/maximum_offset/timeout が source から伝播される."""
        source = estat_source(
            tables=[
                estat_table(
                    stats_data_id="0000020201",
                    app_id="test_app_id",
                    table_name="pop",
                ),
            ],
            app_id="test_app_id",
            limit=50000,
            maximum_offset=200000,
            timeout=120,
        )
        for resource in source.resources.values():
            assert resource.explicit_args.get("limit") == 50000
            assert resource.explicit_args.get("maximum_offset") == 200000
            assert resource.explicit_args.get("timeout") == 120

    def test_tables_and_stats_data_ids_raises(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            estat_source(
                stats_data_ids="0000020201",
                tables=[
                    estat_table(
                        stats_data_id="0000020201",
                        app_id="test_app_id",
                    ),
                ],
                app_id="test_app_id",
            )

    def test_empty_tables_raises(self):
        with pytest.raises(ValueError, match="tables must not be empty"):
            estat_source(tables=[], app_id="test_app_id")

    def test_neither_tables_nor_stats_data_ids_raises(self):
        with pytest.raises(ValueError, match="Either stats_data_ids or tables"):
            estat_source(app_id="test_app_id")

    def test_tables_with_write_disposition_raises(self):
        with pytest.raises(ValueError, match="write_disposition"):
            estat_source(
                tables=[
                    estat_table(
                        stats_data_id="0000020201",
                        app_id="test_app_id",
                        table_name="pop",
                    ),
                ],
                app_id="test_app_id",
                write_disposition="merge",
            )

    def test_tables_with_primary_key_raises(self):
        with pytest.raises(ValueError, match="primary_key"):
            estat_source(
                tables=[
                    estat_table(
                        stats_data_id="0000020201",
                        app_id="test_app_id",
                        table_name="pop",
                    ),
                ],
                app_id="test_app_id",
                primary_key=["time", "area"],
            )

    def test_tables_with_incremental_raises(self):
        with pytest.raises(ValueError, match="incremental"):
            estat_source(
                tables=[
                    estat_table(
                        stats_data_id="0000020201",
                        app_id="test_app_id",
                        table_name="pop",
                    ),
                ],
                app_id="test_app_id",
                incremental=dlt.sources.incremental("time"),
            )

    def test_tables_with_api_params_raises(self):
        with pytest.raises(ValueError, match="api_params"):
            estat_source(
                tables=[
                    estat_table(
                        stats_data_id="0000020201",
                        app_id="test_app_id",
                        table_name="pop",
                    ),
                ],
                app_id="test_app_id",
                lang="J",
            )

    def test_tables_with_default_args_succeeds(self):
        """tables mode with all default values should succeed."""
        source = estat_source(
            tables=[
                estat_table(
                    stats_data_id="0000020201",
                    app_id="test_app_id",
                    table_name="pop",
                ),
            ],
            app_id="test_app_id",
        )
        assert "pop" in source.resources


class TestEstatSourceIncremental:
    """Tests for estat_source incremental loading."""

    def test_incremental_passed_to_all_resources(self):
        source = estat_source(
            stats_data_ids=["0000020201", "0004028584"],
            app_id="test_app_id",
            write_disposition="merge",
            primary_key=["time", "area"],
            incremental=dlt.sources.incremental("time", initial_value="0000000000"),
        )
        for resource in source.resources.values():
            sig = inspect.signature(resource._pipe.gen.__wrapped__)  # type: ignore[union-attr]
            default = sig.parameters["time_incremental"].default
            assert isinstance(default, dlt.sources.incremental)

    def test_incremental_none_by_default(self):
        source = estat_source(
            stats_data_ids="0000020201",
            app_id="test_app_id",
        )
        for resource in source.resources.values():
            sig = inspect.signature(resource._pipe.gen.__wrapped__)  # type: ignore[union-attr]
            default = sig.parameters["time_incremental"].default
            assert default is None
