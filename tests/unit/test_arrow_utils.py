"""Tests for arrow utility functions."""

from typing import Optional

import pyarrow as pa
import pytest
from pydantic import BaseModel

from estat_api_dlt_helper.utils import create_arrow_struct_type, model_to_arrow_dict


class SimpleModel(BaseModel):
    """Simple test model."""
    name: str
    age: int
    score: float
    active: bool


class NestedModel(BaseModel):
    """Model with nested structure."""
    id: str
    details: SimpleModel
    count: int


class OptionalModel(BaseModel):
    """Model with optional fields."""
    required_field: str
    optional_field: Optional[int] = None
    optional_nested: Optional[SimpleModel] = None


class TestCreateArrowStructType:
    """Test cases for create_arrow_struct_type function."""
    
    def test_simple_model_struct(self):
        """Test creating struct type from simple model."""
        struct_type = create_arrow_struct_type(SimpleModel)
        
        assert isinstance(struct_type, pa.StructType)
        assert len(struct_type) == 4
        
        # Check field types
        fields = {field.name: field.type for field in struct_type}
        assert fields["name"] == pa.string()
        assert fields["age"] == pa.int64()
        assert fields["score"] == pa.float64()
        assert fields["active"] == pa.bool_()
    
    def test_nested_model_struct(self):
        """Test creating struct type from nested model."""
        struct_type = create_arrow_struct_type(NestedModel)
        
        assert isinstance(struct_type, pa.StructType)
        assert len(struct_type) == 3
        
        # Check nested field
        fields = {field.name: field.type for field in struct_type}
        assert fields["id"] == pa.string()
        assert fields["count"] == pa.int64()
        assert isinstance(fields["details"], pa.StructType)
        
        # Check nested struct fields
        nested_fields = {field.name: field.type for field in fields["details"]}
        assert nested_fields["name"] == pa.string()
        assert nested_fields["age"] == pa.int64()
    
    def test_optional_fields_struct(self):
        """Test creating struct type with optional fields."""
        struct_type = create_arrow_struct_type(OptionalModel)
        
        fields = {field.name: field.type for field in struct_type}
        assert fields["required_field"] == pa.string()
        assert fields["optional_field"] == pa.int64()  # Optional is unwrapped
        assert isinstance(fields["optional_nested"], pa.StructType)


class TestModelToArrowDict:
    """Test cases for model_to_arrow_dict function."""
    
    def test_simple_model_conversion(self):
        """Test converting simple model to dict."""
        model = SimpleModel(
            name="Test",
            age=25,
            score=95.5,
            active=True
        )
        
        result = model_to_arrow_dict(model)
        assert result == {
            "name": "Test",
            "age": 25,
            "score": 95.5,
            "active": True
        }
    
    def test_nested_model_conversion(self):
        """Test converting nested model to dict."""
        model = NestedModel(
            id="123",
            details=SimpleModel(
                name="Nested",
                age=30,
                score=88.0,
                active=False
            ),
            count=5
        )
        
        result = model_to_arrow_dict(model)
        assert result["id"] == "123"
        assert result["count"] == 5
        assert isinstance(result["details"], dict)
        assert result["details"]["name"] == "Nested"
        assert result["details"]["age"] == 30
    
    def test_model_with_none_values(self):
        """Test converting model with None values."""
        model = OptionalModel(
            required_field="Required",
            optional_field=None,
            optional_nested=None
        )
        
        result = model_to_arrow_dict(model)
        assert result["required_field"] == "Required"
        assert result["optional_field"] is None
        assert result["optional_nested"] is None
    
    def test_model_with_optional_values(self):
        """Test converting model with optional values set."""
        model = OptionalModel(
            required_field="Required",
            optional_field=42,
            optional_nested=SimpleModel(
                name="Optional",
                age=20,
                score=75.0,
                active=True
            )
        )
        
        result = model_to_arrow_dict(model)
        assert result["required_field"] == "Required"
        assert result["optional_field"] == 42
        assert isinstance(result["optional_nested"], dict)
        assert result["optional_nested"]["name"] == "Optional"