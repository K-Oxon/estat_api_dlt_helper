"""Tests for the data models."""

import pytest

from estat_api_dlt_helper.models import (
    ClassAttributes,
    ClassInfModel,
    ClassModel,
    ClassObjModel,
    CodeValue,
    Description,
    StatisticsNameSpec,
    TableInf,
    Title,
    TitleSpec,
)


class TestClassAttributes:
    """Test cases for ClassAttributes model."""
    
    def test_basic_attributes(self):
        """Test basic attribute parsing."""
        data = {
            "@code": "01100",
            "@name": "北海道 札幌市",
            "@level": "2",
            "@unit": "人"
        }
        
        attrs = ClassAttributes.model_validate(data)
        assert attrs.code == "01100"
        assert attrs.name == "北海道 札幌市"
        assert attrs.level == "2"
        assert attrs.unit == "人"
        assert attrs.parent_code is None
    
    def test_extra_attributes(self):
        """Test extraction of extra attributes."""
        data = {
            "@code": "01100",
            "@name": "北海道 札幌市",
            "@customField": "custom_value",
            "@anotherField": "another_value"
        }
        
        attrs = ClassAttributes.model_validate(data)
        assert attrs.code == "01100"
        assert attrs.name == "北海道 札幌市"
        assert attrs.extra_attributes == {
            "customField": "custom_value",
            "anotherField": "another_value"
        }
    
    def test_minimal_attributes(self):
        """Test with only required attributes."""
        data = {
            "@code": "001",
            "@name": "Test"
        }
        
        attrs = ClassAttributes.model_validate(data)
        assert attrs.code == "001"
        assert attrs.name == "Test"
        assert attrs.level is None
        assert attrs.unit is None
        assert attrs.parent_code is None
        assert attrs.extra_attributes == {}


class TestClassModel:
    """Test cases for ClassModel."""
    
    def test_class_model_creation(self):
        """Test ClassModel creation from dict."""
        data = {
            "@code": "01100",
            "@name": "北海道 札幌市",
            "@level": "2"
        }
        
        model = ClassModel.model_validate(data)
        assert model.attributes.code == "01100"
        assert model.attributes.name == "北海道 札幌市"
        assert model.attributes.level == "2"


class TestClassObjModel:
    """Test cases for ClassObjModel."""
    
    def test_single_class_to_list(self):
        """Test that single CLASS is converted to list."""
        data = {
            "@id": "area",
            "@name": "地域",
            "CLASS": {
                "@code": "01100",
                "@name": "北海道 札幌市"
            }
        }
        
        obj = ClassObjModel.model_validate(data)
        assert obj.id == "area"
        assert obj.name == "地域"
        assert isinstance(obj.class_info, list)
        assert len(obj.class_info) == 1
        assert obj.class_info[0].attributes.code == "01100"
    
    def test_multiple_classes(self):
        """Test with multiple CLASS entries."""
        data = {
            "@id": "area",
            "@name": "地域",
            "CLASS": [
                {"@code": "01100", "@name": "北海道 札幌市"},
                {"@code": "01101", "@name": "北海道 札幌市 中央区"}
            ]
        }
        
        obj = ClassObjModel.model_validate(data)
        assert len(obj.class_info) == 2
        assert obj.class_info[0].attributes.code == "01100"
        assert obj.class_info[1].attributes.code == "01101"


class TestTableInf:
    """Test cases for TableInf model."""
    
    def test_complete_table_inf(self):
        """Test TableInf with all fields."""
        data = {
            "@id": "0000020201",
            "STAT_NAME": {"@code": "00200502", "$": "社会・人口統計体系"},
            "GOV_ORG": {"@code": "00200", "$": "総務省"},
            "STATISTICS_NAME": "市区町村データ",
            "TITLE": {"@no": "0000020201", "$": "Ａ　人口・世帯"},
            "CYCLE": "年度次",
            "SURVEY_DATE": "0",
            "OPEN_DATE": "2024-06-21",
            "SMALL_AREA": 0,
            "COLLECT_AREA": "市区町村",
            "MAIN_CATEGORY": {"@code": "99", "$": "その他"},
            "SUB_CATEGORY": {"@code": "99", "$": "その他"},
            "OVERALL_TOTAL_NUMBER": 1830033,
            "UPDATED_DATE": "2024-06-21",
            "STATISTICS_NAME_SPEC": {
                "TABULATION_CATEGORY": "市区町村データ",
                "TABULATION_SUB_CATEGORY1": "基礎データ"
            },
            "DESCRIPTION": {
                "TABULATION_CATEGORY_EXPLANATION": "説明文"
            },
            "TITLE_SPEC": {
                "TABLE_NAME": "Ａ　人口・世帯"
            }
        }
        
        table_inf = TableInf.model_validate(data)
        assert table_inf.id == "0000020201"
        assert table_inf.stat_name.code == "00200502"
        assert table_inf.stat_name.value == "社会・人口統計体系"
        assert table_inf.statistics_name == "市区町村データ"
        assert table_inf.cycle == "年度次"
        assert table_inf.survey_date == "0"
        assert table_inf.overall_total_number == 1830033
    
    def test_table_inf_with_string_small_area(self):
        """Test TableInf with string small_area field."""
        data = {
            "@id": "0000020201",
            "STAT_NAME": {"@code": "00200502", "$": "社会・人口統計体系"},
            "GOV_ORG": {"@code": "00200", "$": "総務省"},
            "STATISTICS_NAME": "市区町村データ",
            "TITLE": {"@no": "0000020201", "$": "Ａ　人口・世帯"},
            "CYCLE": "年度次",
            "SURVEY_DATE": "2024",
            "OPEN_DATE": "2024-06-21",
            "SMALL_AREA": "対象",
            "COLLECT_AREA": "市区町村",
            "MAIN_CATEGORY": {"@code": "99", "$": "その他"},
            "SUB_CATEGORY": {"@code": "99", "$": "その他"},
            "OVERALL_TOTAL_NUMBER": 1830033,
            "UPDATED_DATE": "2024-06-21",
            "STATISTICS_NAME_SPEC": {
                "TABULATION_CATEGORY": "市区町村データ",
                "TABULATION_SUB_CATEGORY1": "基礎データ"
            },
            "DESCRIPTION": {
                "TABULATION_CATEGORY_EXPLANATION": "説明文"
            },
            "TITLE_SPEC": {
                "TABLE_NAME": "Ａ　人口・世帯"
            }
        }
        
        table_inf = TableInf.model_validate(data)
        assert table_inf.small_area == "対象"
        assert table_inf.survey_date == "2024"
    
    def test_table_inf_with_string_description(self):
        """Test TableInf with string description field."""
        data = {
            "@id": "0000020201",
            "STAT_NAME": {"@code": "00200502", "$": "社会・人口統計体系"},
            "GOV_ORG": {"@code": "00200", "$": "総務省"},
            "STATISTICS_NAME": "市区町村データ",
            "TITLE": {"@no": "0000020201", "$": "Ａ　人口・世帯"},
            "CYCLE": "年度次",
            "SURVEY_DATE": "0",
            "OPEN_DATE": "2024-06-21",
            "SMALL_AREA": 0,
            "COLLECT_AREA": "市区町村",
            "MAIN_CATEGORY": {"@code": "99", "$": "その他"},
            "SUB_CATEGORY": {"@code": "99", "$": "その他"},
            "OVERALL_TOTAL_NUMBER": 1830033,
            "UPDATED_DATE": "2024-06-21",
            "STATISTICS_NAME_SPEC": {
                "TABULATION_CATEGORY": "市区町村データ",
                "TABULATION_SUB_CATEGORY1": "基礎データ"
            },
            "DESCRIPTION": "シンプルな説明文",
            "TITLE_SPEC": {
                "TABLE_NAME": "Ａ　人口・世帯"
            }
        }
        
        table_inf = TableInf.model_validate(data)
        assert table_inf.description == "シンプルな説明文"
        assert isinstance(table_inf.description, str)
    
    def test_table_inf_with_int_survey_date(self):
        """Test TableInf with integer survey_date field."""
        data = {
            "@id": "0000020201",
            "STAT_NAME": {"@code": "00200502", "$": "社会・人口統計体系"},
            "GOV_ORG": {"@code": "00200", "$": "総務省"},
            "STATISTICS_NAME": "市区町村データ",
            "TITLE": {"@no": "0000020201", "$": "Ａ　人口・世帯"},
            "CYCLE": "年度次",
            "SURVEY_DATE": 2024,  # Integer value
            "OPEN_DATE": "2024-06-21",
            "SMALL_AREA": 0,
            "COLLECT_AREA": "市区町村",
            "MAIN_CATEGORY": {"@code": "99", "$": "その他"},
            "SUB_CATEGORY": {"@code": "99", "$": "その他"},
            "OVERALL_TOTAL_NUMBER": 1830033,
            "UPDATED_DATE": "2024-06-21",
            "STATISTICS_NAME_SPEC": {
                "TABULATION_CATEGORY": "市区町村データ",
                "TABULATION_SUB_CATEGORY1": "基礎データ"
            },
            "DESCRIPTION": {
                "TABULATION_CATEGORY_EXPLANATION": "説明文"
            },
            "TITLE_SPEC": {
                "TABLE_NAME": "Ａ　人口・世帯"
            }
        }
        
        table_inf = TableInf.model_validate(data)
        assert table_inf.survey_date == 2024
        assert isinstance(table_inf.survey_date, int)


class TestCodeValue:
    """Test cases for CodeValue model."""
    
    def test_code_value_parsing(self):
        """Test CodeValue parsing."""
        data = {"@code": "001", "$": "Test Value"}
        
        cv = CodeValue.model_validate(data)
        assert cv.code == "001"
        assert cv.value == "Test Value"