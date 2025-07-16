"""Tests for the arrow converter module."""

import pyarrow as pa
import pytest

from estat_api_dlt_helper.models import ClassInfModel
from estat_api_dlt_helper.parser.arrow_converter import ArrowConverter
from estat_api_dlt_helper.parser.metadata_processor import MetadataProcessor


@pytest.fixture
def metadata_processor():
    """Create a MetadataProcessor instance."""
    return MetadataProcessor()


@pytest.fixture
def arrow_converter(metadata_processor):
    """Create an ArrowConverter instance."""
    return ArrowConverter(metadata_processor)


@pytest.fixture
def statistical_data(sample_response_data):
    """Extract statistical data from sample response."""
    return sample_response_data["GET_STATS_DATA"]["STATISTICAL_DATA"]


class TestArrowConverter:
    """Test cases for ArrowConverter."""
    
    def test_extract_value_columns(self, arrow_converter):
        """Test extracting column names from value data."""
        values = [
            {
                "@tab": "00001",
                "@cat01": "A2101",
                "@area": "01100",
                "@time": "2020100000",
                "@unit": "人",
                "$": "1973395"
            }
        ]
        
        columns = arrow_converter._extract_value_columns(values)
        
        assert "tab" in columns
        assert "cat01" in columns
        assert "area" in columns
        assert "time" in columns
        assert "unit" in columns
        assert "value" in columns
        assert len(columns) == 6
    
    def test_extract_value_columns_empty(self, arrow_converter):
        """Test extracting columns from empty data."""
        columns = arrow_converter._extract_value_columns([])
        assert columns == []
    
    def test_parse_numeric_value(self, arrow_converter):
        """Test parsing various numeric values."""
        # Normal number
        assert arrow_converter._parse_numeric_value("123") == 123.0
        assert arrow_converter._parse_numeric_value("123.45") == 123.45
        
        # Number with commas (Japanese format)
        assert arrow_converter._parse_numeric_value("1,234,567") == 1234567.0
        
        # Invalid values
        assert arrow_converter._parse_numeric_value("N/A") is None
        assert arrow_converter._parse_numeric_value("") is None
        assert arrow_converter._parse_numeric_value(None) is None
        assert arrow_converter._parse_numeric_value("abc") is None
    
    def test_convert_to_arrow_basic(self, arrow_converter, statistical_data):
        """Test basic Arrow conversion."""
        table = arrow_converter.convert_to_arrow(statistical_data)
        
        # Check table structure
        assert isinstance(table, pa.Table)
        assert len(table) == len(statistical_data["DATA_INF"]["VALUE"])
        
        # Check required columns exist
        expected_columns = {
            "tab", "cat01", "area", "time", "unit", "value",
            "tab_metadata", "cat01_metadata", "area_metadata", "stat_inf"
        }
        assert set(table.column_names).issuperset(expected_columns)
        
        # Check data types
        assert pa.types.is_float64(table.schema.field("value").type)
        assert pa.types.is_string(table.schema.field("area").type)
        assert pa.types.is_struct(table.schema.field("area_metadata").type)
        assert pa.types.is_struct(table.schema.field("stat_inf").type)
    
    def test_convert_to_arrow_metadata_content(self, arrow_converter, statistical_data):
        """Test metadata content in converted table."""
        table = arrow_converter.convert_to_arrow(statistical_data)
        
        # Get first row
        first_row = table.slice(0, 1)
        
        # Check area metadata
        area_metadata = first_row["area_metadata"][0].as_py()
        assert area_metadata["code"] == "01100"
        assert area_metadata["name"] == "北海道 札幌市"
        assert area_metadata["level"] == "2"
        assert area_metadata["parent_code"] == "01000"
        
        # Check value
        value = first_row["value"][0].as_py()
        assert value == 1973395.0
        
        # Check stat_inf is same for all rows
        stat_inf_col = table["stat_inf"].to_pylist()
        assert all(row == stat_inf_col[0] for row in stat_inf_col)
    
    def test_convert_to_arrow_with_invalid_values(self, arrow_converter, statistical_data):
        """Test conversion with invalid numeric values."""
        # Modify data to include invalid value
        modified_data = statistical_data.copy()
        modified_data["DATA_INF"]["VALUE"][0]["$"] = "not_a_number"
        
        table = arrow_converter.convert_to_arrow(modified_data)
        
        # First value should be None
        assert table["value"][0].as_py() is None
        # Second value should still be valid
        assert table["value"][1].as_py() == 248680.0
    
    def test_dynamic_categories(self, arrow_converter, statistical_data):
        """Test handling of dynamic categories."""
        # Add new category to data
        modified_data = statistical_data.copy()
        
        # Add cat02 to values
        for value in modified_data["DATA_INF"]["VALUE"]:
            value["@cat02"] = "TEST_CAT"
        
        # Add corresponding metadata
        modified_data["CLASS_INF"]["CLASS_OBJ"].append({
            "@id": "cat02",
            "@name": "テストカテゴリ",
            "CLASS": {
                "@code": "TEST_CAT",
                "@name": "テストカテゴリ値",
                "@level": "1"
            }
        })
        
        table = arrow_converter.convert_to_arrow(modified_data)
        
        # Check new columns exist
        assert "cat02" in table.column_names
        assert "cat02_metadata" in table.column_names
        
        # Check metadata content
        cat02_metadata = table["cat02_metadata"][0].as_py()
        assert cat02_metadata["code"] == "TEST_CAT"
        assert cat02_metadata["name"] == "テストカテゴリ値"
    
    def test_missing_metadata_handling(self, arrow_converter, statistical_data):
        """Test handling of missing metadata for a code."""
        # Add a value with a code that doesn't have metadata
        modified_data = statistical_data.copy()
        modified_data["DATA_INF"]["VALUE"].append({
            "@tab": "00001",
            "@cat01": "A2101",
            "@area": "99999",  # Non-existent area code
            "@time": "2020100000",
            "@unit": "人",
            "$": "100"
        })
        
        table = arrow_converter.convert_to_arrow(modified_data)
        
        # Check last row has None values for metadata fields
        last_row_metadata = table["area_metadata"][-1].as_py()
        # Should have None values for all fields when metadata is missing
        assert last_row_metadata["code"] is None
        assert last_row_metadata["name"] is None
        assert last_row_metadata["level"] is None
        assert last_row_metadata["parent_code"] is None
    
    def test_table_info_consistency(self, arrow_converter, statistical_data):
        """Test that table info is consistent across all rows."""
        table = arrow_converter.convert_to_arrow(statistical_data)
        
        # Get stat_inf column
        stat_inf_list = table["stat_inf"].to_pylist()
        
        # All rows should have identical stat_inf
        first_stat_inf = stat_inf_list[0]
        for stat_inf in stat_inf_list[1:]:
            assert stat_inf == first_stat_inf
        
        # Check some specific fields
        assert first_stat_inf["id"] == "0000020201"
        assert first_stat_inf["statistics_name"] == "市区町村データ 基礎データ（廃置分合処理済）"
        assert first_stat_inf["cycle"] == "年度次"
    
    def test_empty_value_data(self, arrow_converter):
        """Test handling of empty VALUE data."""
        empty_data = {
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
                "OVERALL_TOTAL_NUMBER": 0,
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
                "CLASS_OBJ": []
            },
            "DATA_INF": {
                "VALUE": []
            }
        }
        
        table = arrow_converter.convert_to_arrow(empty_data)
        
        assert isinstance(table, pa.Table)
        assert len(table) == 0