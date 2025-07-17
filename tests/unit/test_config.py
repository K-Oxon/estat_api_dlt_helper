"""Tests for configuration models."""

import pytest
from pydantic import ValidationError

from estat_api_dlt_helper.config import DestinationConfig, EstatDltConfig, SourceConfig


class TestSourceConfig:
    """Tests for SourceConfig model."""

    def test_basic_source_config(self):
        """Test basic SourceConfig creation."""
        config = SourceConfig(
            app_id="test_api_key",
            statsDataId="0000010111",
        )
        assert config.app_id == "test_api_key"
        assert config.statsDataId == "0000010111"
        assert config.lang == "J"  # default
        assert config.metaGetFlg == "Y"  # default
        assert config.cntGetFlg == "N"  # default
        assert config.limit == 100000  # default

    def test_social_demographic_params(self):
        """Test SourceConfig with social demographic parameters."""
        # social_and_demographic_pref_basic.py を参考にしたパラメータ
        config = SourceConfig(
            app_id="test_api_key",
            statsDataId="0000010111",  # K 安全
            lang="J",
            metaGetFlg="Y",
            cntGetFlg="N",
            explanationGetFlg="Y",
            annotationGetFlg="Y",
            replaceSpChars="2",
        )
        assert config.statsDataId == "0000010111"
        assert config.explanationGetFlg == "Y"
        assert config.annotationGetFlg == "Y"
        assert config.replaceSpChars == "2"

    def test_multiple_stats_data_ids(self):
        """Test SourceConfig with multiple statsDataId."""
        config = SourceConfig(
            app_id="test_api_key",
            statsDataId=["0000010101", "0000010102", "0000010103"],  # A, B, C
        )
        assert isinstance(config.statsDataId, list)
        assert len(config.statsDataId) == 3

    def test_extra_params_allowed(self):
        """Test that extra parameters (like cdCat01) are allowed."""
        config = SourceConfig(
            app_id="test_api_key",
            statsDataId="0000010111",
            cdCat01="A1101,A110101,A110102",  # カテゴリコード
            cdTime="2023100000",  # 時間コード
        )
        assert config.cdCat01 == "A1101,A110101,A110102"  # type: ignore
        assert config.cdTime == "2023100000"  # type: ignore

    def test_invalid_stats_data_id(self):
        """Test validation errors for invalid statsDataId."""
        with pytest.raises(ValidationError) as exc_info:
            SourceConfig(
                app_id="test_api_key",
                statsDataId="",  # empty string
            )
        assert "statsDataId cannot be empty" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            SourceConfig(
                app_id="test_api_key",
                statsDataId=[],  # empty list
            )
        assert "statsDataId list cannot be empty" in str(exc_info.value)

    def test_pagination_params(self):
        """Test pagination parameters."""
        config = SourceConfig(
            app_id="test_api_key",
            statsDataId="0000010111",
            limit=1000,
            maximum_offset=5000,
        )
        assert config.limit == 1000
        assert config.maximum_offset == 5000


class TestDestinationConfig:
    """Tests for DestinationConfig model."""

    def test_basic_duckdb_config(self):
        """Test basic DestinationConfig for DuckDB."""
        config = DestinationConfig(
            destination="duckdb",
            dataset_name="social_demographic",
            table_name="pref_safety_data",
        )
        assert config.destination == "duckdb"
        assert config.dataset_name == "social_demographic"
        assert config.table_name == "pref_safety_data"
        assert config.write_disposition == "merge"  # default
        assert config.primary_key == ["time", "area", "cat01"]  # default

    def test_custom_primary_key(self):
        """Test custom primary key configuration."""
        config = DestinationConfig(
            destination="duckdb",
            dataset_name="test_dataset",
            table_name="test_table",
            primary_key=["custom_id", "timestamp"],
        )
        assert config.primary_key == ["custom_id", "timestamp"]

    def test_append_disposition(self):
        """Test append write disposition."""
        config = DestinationConfig(
            destination="duckdb",
            dataset_name="test_dataset",
            table_name="test_table",
            write_disposition="append",
            primary_key=None,  # not required for append
        )
        assert config.write_disposition == "append"
        assert config.primary_key is None

    def test_merge_requires_primary_key(self):
        """Test that merge disposition requires primary key."""
        with pytest.raises(ValidationError) as exc_info:
            DestinationConfig(
                destination="duckdb",
                dataset_name="test_dataset",
                table_name="test_table",
                write_disposition="merge",
                primary_key=None,  # this should fail
            )
        assert "primary_key must be specified when write_disposition is 'merge'" in str(
            exc_info.value
        )

    def test_pipeline_options(self):
        """Test pipeline configuration options."""
        config = DestinationConfig(
            destination="duckdb",
            dataset_name="test_dataset",
            table_name="test_table",
            pipeline_name="custom_pipeline",
            dev_mode=True,
        )
        assert config.pipeline_name == "custom_pipeline"
        assert config.dev_mode is True


class TestEstatDltConfig:
    """Tests for EstatDltConfig model."""

    def test_complete_config(self):
        """Test complete EstatDltConfig creation."""
        config = EstatDltConfig(
            source={
                "app_id": "test_api_key",
                "statsDataId": "0000010111",
                "lang": "J",
                "metaGetFlg": "Y",
                "cntGetFlg": "N",
            },
            destination={
                "destination": "duckdb",
                "dataset_name": "social_demographic",
                "table_name": "pref_safety_data",
                "write_disposition": "merge",
                "primary_key": ["time", "area", "cat01"],
            },
        )
        assert config.source.app_id == "test_api_key"
        assert config.source.statsDataId == "0000010111"
        assert config.destination.destination == "duckdb"
        assert config.destination.dataset_name == "social_demographic"

    def test_config_with_processing_options(self):
        """Test config with processing options."""
        config = EstatDltConfig(
            source={
                "app_id": "test_api_key",
                "statsDataId": "0000010111",
            },
            destination={
                "destination": "duckdb",
                "dataset_name": "test_dataset",
                "table_name": "test_table",
            },
            batch_size=5000,
            max_retries=5,
            timeout=300,
            flatten_metadata=True,
            include_api_metadata=False,
        )
        assert config.batch_size == 5000
        assert config.max_retries == 5
        assert config.timeout == 300
        assert config.flatten_metadata is True
        assert config.include_api_metadata is False

    def test_config_dict_style(self):
        """Test creating config from dictionary (as shown in concept.md)."""
        config_dict = {
            "source": {
                "app_id": "YOUR-KEY",
                "statsDataId": "0000020211",
                "limit": 10,
            },
            "destination": {
                "destination": "duckdb",
                "dataset_name": "demo",
                "table_name": "demo",
                "write_disposition": "merge",
                "primary_key": ["time", "area", "cat01"],
            },
        }
        config = EstatDltConfig(**config_dict)
        assert config.source.app_id == "YOUR-KEY"
        assert config.source.statsDataId == "0000020211"
        assert config.source.limit == 10
        assert config.destination.table_name == "demo"

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden in main config."""
        with pytest.raises(ValidationError):
            EstatDltConfig(
                source={
                    "app_id": "test_api_key",
                    "statsDataId": "0000010111",
                },
                destination={
                    "destination": "duckdb",
                    "dataset_name": "test_dataset",
                    "table_name": "test_table",
                },
                unknown_field="should_fail",  # this should fail
            )

    def test_validate_assignment(self):
        """Test that assignment validation works."""
        config = EstatDltConfig(
            source={
                "app_id": "test_api_key",
                "statsDataId": "0000010111",
            },
            destination={
                "destination": "duckdb",
                "dataset_name": "test_dataset",
                "table_name": "test_table",
            },
        )
        # This should work due to validate_assignment=True
        config.max_retries = 10
        assert config.max_retries == 10
