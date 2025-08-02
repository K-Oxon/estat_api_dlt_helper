"""Unified schema models for handling different metadata structures across stats IDs."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class UnifiedTimeMetadata(BaseModel):
    """Unified time metadata that includes all possible fields."""

    code: str = Field(description="Time code")
    name: str = Field(description="Time name")
    level: Optional[str] = Field(None, description="Time level")
    parent_code: Optional[str] = Field(None, description="Parent time code")
    unit: Optional[str] = Field(None, description="Time unit")
    extra_attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes"
    )


class UnifiedCategoryMetadata(BaseModel):
    """Unified category metadata that includes all possible fields."""

    code: str = Field(description="Category code")
    name: str = Field(description="Category name")
    level: Optional[str] = Field(None, description="Category level")
    parent_code: Optional[str] = Field(None, description="Parent category code")
    unit: Optional[str] = Field(None, description="Category unit")
    extra_attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes"
    )


class UnifiedTabMetadata(BaseModel):
    """Unified table metadata that includes all possible fields."""

    code: str = Field(description="Table code")
    name: str = Field(description="Table name")
    level: Optional[str] = Field(None, description="Table level")
    unit: Optional[str] = Field(None, description="Table unit")
    parent_code: Optional[str] = Field(None, description="Parent table code")
    extra_attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes"
    )


class UnifiedAreaMetadata(BaseModel):
    """Unified area metadata that includes all possible fields."""

    code: str = Field(description="Area code")
    name: str = Field(description="Area name")
    level: Optional[str] = Field(None, description="Area level")
    parent_code: Optional[str] = Field(None, description="Parent area code")
    extra_attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes"
    )


class UnifiedStatInf(BaseModel):
    """Unified statistical information metadata."""

    id: str = Field(description="Statistics ID")
    stat_name: Dict[str, str] = Field(description="Statistics name")
    gov_org: Dict[str, str] = Field(description="Government organization")
    statistics_name: str = Field(description="Statistics name")
    title: str = Field(description="Title")
    cycle: str = Field(description="Cycle")
    survey_date: str = Field(description="Survey date")
    open_date: str = Field(description="Open date")
    small_area: str = Field(description="Small area")
    collect_area: str = Field(description="Collection area")
    main_category: Dict[str, str] = Field(description="Main category")
    sub_category: Dict[str, str] = Field(description="Sub category")
    overall_total_number: int = Field(description="Overall total number")
    updated_date: str = Field(description="Updated date")
    statistics_name_spec: Dict[str, Optional[str]] = Field(
        description="Statistics name specification"
    )
    description: str = Field(description="Description")
    title_spec: Dict[str, str] = Field(description="Title specification")


class UnifiedEstatRecord(BaseModel):
    """Unified record model that can handle all possible estat data structures."""

    # Value columns - these are dynamic but common ones
    tab: Optional[str] = Field(None, description="Table code")
    cat01: Optional[str] = Field(None, description="Category 01 code")
    cat02: Optional[str] = Field(None, description="Category 02 code")
    cat03: Optional[str] = Field(None, description="Category 03 code")
    cat04: Optional[str] = Field(None, description="Category 04 code")
    cat05: Optional[str] = Field(None, description="Category 05 code")
    cat06: Optional[str] = Field(None, description="Category 06 code")
    cat07: Optional[str] = Field(None, description="Category 07 code")
    cat08: Optional[str] = Field(None, description="Category 08 code")
    cat09: Optional[str] = Field(None, description="Category 09 code")
    cat10: Optional[str] = Field(None, description="Category 10 code")
    cat11: Optional[str] = Field(None, description="Category 11 code")
    cat12: Optional[str] = Field(None, description="Category 12 code")
    cat13: Optional[str] = Field(None, description="Category 13 code")
    cat14: Optional[str] = Field(None, description="Category 14 code")
    cat15: Optional[str] = Field(None, description="Category 15 code")
    area: Optional[str] = Field(None, description="Area code")
    time: Optional[str] = Field(None, description="Time code")
    unit: Optional[str] = Field(None, description="Unit")
    value: Optional[float] = Field(None, description="Statistical value")

    # Metadata columns - unified structure
    tab_metadata: Optional[UnifiedTabMetadata] = Field(
        None, description="Table metadata"
    )
    cat01_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 01 metadata"
    )
    cat02_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 02 metadata"
    )
    cat03_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 03 metadata"
    )
    cat04_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 04 metadata"
    )
    cat05_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 05 metadata"
    )
    cat06_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 06 metadata"
    )
    cat07_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 07 metadata"
    )
    cat08_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 08 metadata"
    )
    cat09_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 09 metadata"
    )
    cat10_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 10 metadata"
    )
    cat11_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 11 metadata"
    )
    cat12_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 12 metadata"
    )
    cat13_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 13 metadata"
    )
    cat14_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 14 metadata"
    )
    cat15_metadata: Optional[UnifiedCategoryMetadata] = Field(
        None, description="Category 15 metadata"
    )
    area_metadata: Optional[UnifiedAreaMetadata] = Field(
        None, description="Area metadata"
    )
    time_metadata: Optional[UnifiedTimeMetadata] = Field(
        None, description="Time metadata"
    )

    # Statistical information
    stat_inf: UnifiedStatInf = Field(description="Statistical information")

    # Dynamic fields for unknown columns
    extra_dimensions: Dict[str, Optional[str]] = Field(
        default_factory=dict, description="Additional dimension columns"
    )
    extra_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata columns"
    )

    class Config:
        """Pydantic configuration."""

        extra = "allow"  # Allow additional fields
        validate_assignment = True
