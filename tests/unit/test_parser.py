"""Tests for the parser module."""

import pytest
import pyarrow as pa

from estat_api_dlt_helper import parse_response


class TestParseResponse:
    """Test cases for parse_response function."""
    
    def test_parse_valid_response(self, sample_response_data):
        """Test parsing a valid e-Stat API response."""
        result = parse_response(sample_response_data)
        
        # Check result is an Arrow table
        assert isinstance(result, pa.Table)
        
        # Check number of rows
        assert result.num_rows == 2
        
        # Check columns exist
        expected_columns = [
            "tab", "cat01", "area", "time", "unit", "value",
            "tab_metadata", "cat01_metadata", "area_metadata", "stat_inf"
        ]
        assert set(result.column_names) == set(expected_columns)
        
        # Check value column data
        values = result.column("value").to_pylist()
        assert values == [1973395.0, 248680.0]
        
        # Check string columns
        areas = result.column("area").to_pylist()
        assert areas == ["01100", "01101"]
    
    def test_parse_response_with_metadata(self, sample_response_data):
        """Test that metadata is properly attached to rows."""
        result = parse_response(sample_response_data)
        
        # Check area metadata
        area_metadata = result.column("area_metadata").to_pylist()
        assert len(area_metadata) == 2
        
        # First row metadata
        assert area_metadata[0]["code"] == "01100"
        assert area_metadata[0]["name"] == "北海道 札幌市"
        assert area_metadata[0]["level"] == "2"
        assert area_metadata[0]["parent_code"] == "01000"
        
        # Second row metadata
        assert area_metadata[1]["code"] == "01101"
        assert area_metadata[1]["name"] == "北海道 札幌市 中央区"
        assert area_metadata[1]["level"] == "3"
        assert area_metadata[1]["parent_code"] == "01100"
    
    def test_parse_response_stat_inf(self, sample_response_data):
        """Test that table information is properly included."""
        result = parse_response(sample_response_data)
        
        # Check stat_inf column
        stat_inf = result.column("stat_inf").to_pylist()
        assert len(stat_inf) == 2
        
        # All rows should have the same stat_inf
        assert stat_inf[0] == stat_inf[1]
        
        # Check some fields
        assert stat_inf[0]["id"] == "0000020201"
        assert stat_inf[0]["statistics_name"] == "市区町村データ 基礎データ（廃置分合処理済）"
        assert stat_inf[0]["cycle"] == "年度次"
    
    def test_parse_invalid_response_missing_section(self):
        """Test parsing fails gracefully with missing sections."""
        invalid_data = {"wrong_key": "value"}
        
        with pytest.raises(ValueError, match="missing GET_STATS_DATA"):
            parse_response(invalid_data)
    
    def test_parse_invalid_response_missing_statistical_data(self):
        """Test parsing fails with missing STATISTICAL_DATA."""
        invalid_data = {
            "GET_STATS_DATA": {
                "RESULT": {"STATUS": 0}
            }
        }
        
        with pytest.raises(ValueError, match="missing STATISTICAL_DATA"):
            parse_response(invalid_data)
    
    def test_parse_invalid_response_missing_value_data(self):
        """Test parsing fails with missing VALUE data."""
        invalid_data = {
            "GET_STATS_DATA": {
                "STATISTICAL_DATA": {
                    "TABLE_INF": {},
                    "CLASS_INF": {"CLASS_OBJ": []},
                    "DATA_INF": {}  # Missing VALUE
                }
            }
        }
        
        with pytest.raises(ValueError, match="DATA_INF missing VALUE"):
            parse_response(invalid_data)
    
    def test_parse_response_with_non_numeric_values(self):
        """Test handling of non-numeric values."""
        data = {
            "GET_STATS_DATA": {
                "STATISTICAL_DATA": {
                    "TABLE_INF": {
                        "@id": "test",
                        "STAT_NAME": {"@code": "001", "$": "Test"},
                        "GOV_ORG": {"@code": "001", "$": "Test"},
                        "STATISTICS_NAME": "Test",
                        "TITLE": {"@no": "001", "$": "Test"},
                        "CYCLE": "Test",
                        "SURVEY_DATE": 0,
                        "OPEN_DATE": "2024-01-01",
                        "SMALL_AREA": 0,
                        "COLLECT_AREA": "Test",
                        "MAIN_CATEGORY": {"@code": "01", "$": "Test"},
                        "SUB_CATEGORY": {"@code": "01", "$": "Test"},
                        "OVERALL_TOTAL_NUMBER": 1,
                        "UPDATED_DATE": "2024-01-01",
                        "STATISTICS_NAME_SPEC": {
                            "TABULATION_CATEGORY": "Test",
                            "TABULATION_SUB_CATEGORY1": "Test"
                        },
                        "DESCRIPTION": {
                            "TABULATION_CATEGORY_EXPLANATION": "Test"
                        },
                        "TITLE_SPEC": {
                            "TABLE_NAME": "Test"
                        }
                    },
                    "CLASS_INF": {
                        "CLASS_OBJ": [
                            {
                                "@id": "cat",
                                "@name": "Category",
                                "CLASS": {
                                    "@code": "001",
                                    "@name": "Test Category"
                                }
                            }
                        ]
                    },
                    "DATA_INF": {
                        "VALUE": [
                            {"@cat": "001", "$": "123"},      # Numeric
                            {"@cat": "001", "$": "N/A"},      # Non-numeric
                            {"@cat": "001", "$": ""},         # Empty
                            {"@cat": "001", "$": "123.45"},   # Float
                        ]
                    }
                }
            }
        }
        
        result = parse_response(data)
        values = result.column("value").to_pylist()
        
        assert values[0] == 123.0
        assert values[1] is None  # Non-numeric becomes None
        assert values[2] is None  # Empty becomes None
        assert values[3] == 123.45