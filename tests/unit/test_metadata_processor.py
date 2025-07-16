"""Tests for the metadata processor module."""

import pyarrow as pa
import pytest

from estat_api_dlt_helper.models import ClassInfModel
from estat_api_dlt_helper.parser.metadata_processor import MetadataProcessor


@pytest.fixture
def metadata_processor():
    """Create a MetadataProcessor instance."""
    return MetadataProcessor()


@pytest.fixture
def sample_class_inf_data():
    """Sample CLASS_INF data for testing."""
    return {
        "CLASS_OBJ": [
            {
                "@id": "tab",
                "@name": "観測値",
                "CLASS": {
                    "@code": "00001",
                    "@name": "観測値",
                    "@level": "1"
                }
            },
            {
                "@id": "area",
                "@name": "地域",
                "CLASS": [
                    {
                        "@code": "01100",
                        "@name": "北海道 札幌市",
                        "@level": "2",
                        "@parentCode": "01000"
                    },
                    {
                        "@code": "01101",
                        "@name": "北海道 札幌市 中央区",
                        "@level": "3",
                        "@parentCode": "01100"
                    }
                ]
            },
            {
                "@id": "time",
                "@name": "時間軸",
                "CLASS": {
                    "@code": "2020100000",
                    "@name": "2020年度",
                    "@level": "1"
                }
            }
        ]
    }


@pytest.fixture
def class_inf_model(sample_class_inf_data):
    """Create a ClassInfModel instance from sample data."""
    return ClassInfModel.model_validate(sample_class_inf_data)


class TestMetadataProcessor:
    """Test cases for MetadataProcessor."""
    
    def test_create_metadata_struct_type_basic(self, metadata_processor, class_inf_model):
        """Test creating metadata struct type with basic fields."""
        # Get the area class obj
        area_obj = next(obj for obj in class_inf_model.class_obj if obj.id == "area")
        
        struct_type = metadata_processor._create_metadata_struct_type(area_obj)
        
        # Check it's a struct type
        assert isinstance(struct_type, pa.StructType)
        
        # Check required fields exist
        field_names = struct_type.names
        assert "code" in field_names
        assert "name" in field_names
        assert "level" in field_names
        assert "parent_code" in field_names
        
        # Check field types
        for field in struct_type:
            assert field.type == pa.string()
    
    def test_create_metadata_struct_type_without_optional_fields(self, metadata_processor, class_inf_model):
        """Test struct type for metadata without optional fields."""
        # Get the tab class obj (has no level, unit, parent_code)
        tab_obj = next(obj for obj in class_inf_model.class_obj if obj.id == "tab")
        
        # Modify to ensure no optional fields
        for cls in tab_obj.class_info:
            cls.attributes.level = "1"  # This will be included
        
        struct_type = metadata_processor._create_metadata_struct_type(tab_obj)
        
        field_names = struct_type.names
        assert "code" in field_names
        assert "name" in field_names
        assert "level" in field_names
        assert "unit" not in field_names  # Should not be included
        assert "parent_code" not in field_names  # Should not be included
    
    def test_create_metadata_mapping(self, metadata_processor, class_inf_model):
        """Test creating metadata mapping."""
        area_obj = next(obj for obj in class_inf_model.class_obj if obj.id == "area")
        
        mapping = metadata_processor._create_metadata_mapping(area_obj)
        
        # Check mapping structure
        assert "01100" in mapping
        assert "01101" in mapping
        
        # Check Sapporo data
        sapporo = mapping["01100"]
        assert sapporo["code"] == "01100"
        assert sapporo["name"] == "北海道 札幌市"
        assert sapporo["level"] == "2"
        assert sapporo["parent_code"] == "01000"
        
        # Check Chuo-ku data
        chuo = mapping["01101"]
        assert chuo["code"] == "01101"
        assert chuo["name"] == "北海道 札幌市 中央区"
        assert chuo["level"] == "3"
        assert chuo["parent_code"] == "01100"
    
    def test_process_metadata_complete(self, metadata_processor, class_inf_model):
        """Test complete metadata processing."""
        struct_types, mappings = metadata_processor.process_metadata(class_inf_model)
        
        # Check all expected fields are present
        expected_fields = {"tab", "area", "time"}
        assert set(struct_types.keys()) == expected_fields
        assert set(mappings.keys()) == expected_fields
        
        # Verify area struct has correct fields
        area_struct = struct_types["area"]
        assert area_struct.num_fields >= 4  # code, name, level, parent_code
        
        # Verify time struct has fewer fields (no parent_code)
        time_struct = struct_types["time"]
        time_fields = set(time_struct.names)
        assert "parent_code" not in time_fields
    
    def test_metadata_struct_fields_consistency(self, metadata_processor, class_inf_model):
        """Test that struct fields match actual data attributes."""
        struct_types, _ = metadata_processor.process_metadata(class_inf_model)
        
        # Check time metadata (should have only code, name, level)
        time_struct = struct_types["time"]
        time_fields = set(time_struct.names)
        expected_time_fields = {"code", "name", "level"}
        assert time_fields == expected_time_fields
        
        # Check area metadata (should have code, name, level, parent_code)
        area_struct = struct_types["area"]
        area_fields = set(area_struct.names)
        expected_area_fields = {"code", "name", "level", "parent_code"}
        assert area_fields == expected_area_fields
    
    def test_create_arrow_schema(self, metadata_processor):
        """Test creating complete Arrow schema."""
        value_columns = ["tab", "cat01", "area", "time", "unit", "value"]
        struct_types = {
            "tab": pa.struct([("code", pa.string()), ("name", pa.string())]),
            "cat01": pa.struct([("code", pa.string()), ("name", pa.string())]),
            "area": pa.struct([
                ("code", pa.string()), 
                ("name", pa.string()),
                ("level", pa.string()),
                ("parent_code", pa.string())
            ])
        }
        stat_inf_type = pa.struct([("id", pa.string()), ("cycle", pa.string())])
        
        schema = metadata_processor.create_arrow_schema(
            value_columns, struct_types, stat_inf_type
        )
        
        # Check schema fields
        assert isinstance(schema, pa.Schema)
        
        # Check value columns
        assert schema.field("tab").type == pa.string()
        assert schema.field("cat01").type == pa.string()
        assert schema.field("area").type == pa.string()
        assert schema.field("time").type == pa.string()
        assert schema.field("unit").type == pa.string()
        assert schema.field("value").type == pa.float64()
        
        # Check metadata columns
        assert pa.types.is_struct(schema.field("tab_metadata").type)
        assert pa.types.is_struct(schema.field("cat01_metadata").type)
        assert pa.types.is_struct(schema.field("area_metadata").type)
        
        # Check stat_inf column
        assert pa.types.is_struct(schema.field("stat_inf").type)
    
    def test_dynamic_metadata_fields(self, metadata_processor):
        """Test handling of dynamic extra attributes."""
        data = {
            "CLASS_OBJ": [{
                "@id": "custom",
                "@name": "カスタム",
                "CLASS": [{
                    "@code": "001",
                    "@name": "テスト",
                    "@customField1": "value1",
                    "@customField2": "value2"
                }]
            }]
        }
        
        class_inf = ClassInfModel.model_validate(data)
        struct_types, mappings = metadata_processor.process_metadata(class_inf)
        
        # Check struct has custom fields
        custom_struct = struct_types["custom"]
        field_names = set(custom_struct.names)
        assert "customField1" in field_names
        assert "customField2" in field_names
        
        # Check mapping has custom field values
        custom_mapping = mappings["custom"]["001"]
        assert custom_mapping["customField1"] == "value1"
        assert custom_mapping["customField2"] == "value2"