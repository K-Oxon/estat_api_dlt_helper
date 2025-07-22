from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BaseMetadataModel(BaseModel):
    """Base class for all metadata models with alias support."""

    model_config = ConfigDict(populate_by_name=True)


class ClassAttributes(BaseMetadataModel):
    """Manages dynamic attributes of CLASS elements."""

    code: str = Field(..., alias="@code")
    name: str = Field(..., alias="@name")
    level: Optional[str] = Field(None, alias="@level")
    unit: Optional[str] = Field(None, alias="@unit")
    parent_code: Optional[str] = Field(None, alias="@parentCode")
    extra_attributes: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def extract_extra_attributes(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional attributes starting with @."""
        if not isinstance(values, dict):
            return values

        # Extract unknown @ attributes
        known_attrs = {"@code", "@name", "@level", "@unit", "@parentCode"}
        extra_attrs = {
            k.lstrip("@"): v
            for k, v in values.items()
            if k.startswith("@") and k not in known_attrs
        }

        if extra_attrs:
            values["extra_attributes"] = extra_attrs
        return values


class ClassModel(BaseMetadataModel):
    """Model for CLASS entries."""

    attributes: ClassAttributes

    @model_validator(mode="before")
    @classmethod
    def construct_attributes(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Construct ClassAttributes from dict."""
        if isinstance(values, dict) and "@code" in values:
            values["attributes"] = ClassAttributes.model_validate(values)
        return values


class ClassObjModel(BaseMetadataModel):
    """Model for CLASS_OBJ entries."""

    id: str = Field(..., alias="@id")
    name: str = Field(..., alias="@name")
    class_info: List[ClassModel] = Field(..., alias="CLASS")

    @model_validator(mode="before")
    @classmethod
    def ensure_class_list(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure CLASS is always treated as a list."""
        if isinstance(values, dict) and "CLASS" in values:
            if not isinstance(values["CLASS"], list):
                values["CLASS"] = [values["CLASS"]]
        return values


class ClassInfModel(BaseMetadataModel):
    """Model for entire CLASS_INF section."""

    class_obj: List[ClassObjModel] = Field(..., alias="CLASS_OBJ")


class CodeValue(BaseMetadataModel):
    """Model for code-value pairs."""

    code: str = Field(..., alias="@code")
    value: str = Field(..., alias="$")


class Title(BaseMetadataModel):
    """Model for title information."""

    no: str = Field(..., alias="@no")
    value: str = Field(..., alias="$")


class StatisticsNameSpec(BaseMetadataModel):
    """Model for statistics name specifications."""

    tabulation_category: str = Field(..., alias="TABULATION_CATEGORY")
    tabulation_sub_category1: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY1"
    )
    tabulation_sub_category2: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY2"
    )
    tabulation_sub_category3: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY3"
    )
    tabulation_sub_category4: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY4"
    )
    tabulation_sub_category5: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY5"
    )


class Description(BaseMetadataModel):
    """Model for statistics description."""

    tabulation_category_explanation: Optional[str] = Field(
        None, alias="TABULATION_CATEGORY_EXPLANATION"
    )
    tabulation_sub_category_explanation1: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY_EXPLANATION1"
    )
    tabulation_sub_category_explanation2: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY_EXPLANATION2"
    )
    tabulation_sub_category_explanation3: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY_EXPLANATION3"
    )
    tabulation_sub_category_explanation4: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY_EXPLANATION4"
    )
    tabulation_sub_category_explanation5: Optional[str] = Field(
        None, alias="TABULATION_SUB_CATEGORY_EXPLANATION5"
    )


class TitleSpec(BaseMetadataModel):
    """Model for title specifications."""

    table_name: str = Field(..., alias="TABLE_NAME")


class TableInf(BaseMetadataModel):
    """Model for table information."""

    id: str = Field(..., alias="@id")
    stat_name: CodeValue = Field(..., alias="STAT_NAME")
    gov_org: CodeValue = Field(..., alias="GOV_ORG")
    statistics_name: str = Field(..., alias="STATISTICS_NAME")
    title: Title | str = Field(..., alias="TITLE")
    cycle: str = Field(..., alias="CYCLE")
    survey_date: int | str = Field(..., alias="SURVEY_DATE")
    open_date: str = Field(..., alias="OPEN_DATE")
    small_area: int | str = Field(..., alias="SMALL_AREA")
    collect_area: str = Field(..., alias="COLLECT_AREA")
    main_category: CodeValue = Field(..., alias="MAIN_CATEGORY")
    sub_category: CodeValue = Field(..., alias="SUB_CATEGORY")
    overall_total_number: int = Field(..., alias="OVERALL_TOTAL_NUMBER")
    updated_date: str = Field(..., alias="UPDATED_DATE")
    statistics_name_spec: StatisticsNameSpec = Field(..., alias="STATISTICS_NAME_SPEC")
    description: Description | str = Field(..., alias="DESCRIPTION")
    title_spec: TitleSpec = Field(..., alias="TITLE_SPEC")

    @model_validator(mode="before")
    @classmethod
    def handle_description(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DESCRIPTION field that can be either a dict or empty string."""
        if isinstance(values, dict) and "DESCRIPTION" in values:
            desc = values["DESCRIPTION"]
            # If DESCRIPTION is an empty string, create an empty Description object
            if desc == "":
                values["DESCRIPTION"] = {}
            # If DESCRIPTION is a dict but doesn't follow expected structure, keep it as is
            # The Description model will handle missing fields with Optional
        return values
