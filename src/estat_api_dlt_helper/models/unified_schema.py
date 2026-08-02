"""Unified schema models for handling different metadata structures across stats IDs."""

from typing import Any

from pydantic import BaseModel, Field


class UnifiedTimeMetadata(BaseModel):
    """Unified time metadata that includes all possible fields."""

    code: str = Field(description="Time code")
    name: str = Field(description="Time name")
    level: str | None = Field(None, description="Time level")
    parent_code: str | None = Field(None, description="Parent time code")
    unit: str | None = Field(None, description="Time unit")
    extra_attributes: dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes"
    )


class UnifiedCategoryMetadata(BaseModel):
    """Unified category metadata that includes all possible fields."""

    code: str = Field(description="Category code")
    name: str = Field(description="Category name")
    level: str | None = Field(None, description="Category level")
    parent_code: str | None = Field(None, description="Parent category code")
    unit: str | None = Field(None, description="Category unit")
    extra_attributes: dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes"
    )


class UnifiedTabMetadata(BaseModel):
    """Unified table metadata that includes all possible fields."""

    code: str = Field(description="Table code")
    name: str = Field(description="Table name")
    level: str | None = Field(None, description="Table level")
    unit: str | None = Field(None, description="Table unit")
    parent_code: str | None = Field(None, description="Parent table code")
    extra_attributes: dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes"
    )


class UnifiedAreaMetadata(BaseModel):
    """Unified area metadata that includes all possible fields."""

    code: str = Field(description="Area code")
    name: str = Field(description="Area name")
    level: str | None = Field(None, description="Area level")
    parent_code: str | None = Field(None, description="Parent area code")
    extra_attributes: dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes"
    )


class UnifiedStatInf(BaseModel):
    """Unified statistical information metadata."""

    id: str = Field(description="Statistics ID")
    stat_name: dict[str, str] = Field(description="Statistics name")
    gov_org: dict[str, str] = Field(description="Government organization")
    statistics_name: str = Field(description="Statistics name")
    title: str = Field(description="Title")
    cycle: str = Field(description="Cycle")
    survey_date: str = Field(description="Survey date")
    open_date: str = Field(description="Open date")
    small_area: str = Field(description="Small area")
    collect_area: str = Field(description="Collection area")
    main_category: dict[str, str] = Field(description="Main category")
    sub_category: dict[str, str] = Field(description="Sub category")
    overall_total_number: int = Field(description="Overall total number")
    updated_date: str = Field(description="Updated date")
    statistics_name_spec: dict[str, str | None] = Field(
        description="Statistics name specification"
    )
    description: str = Field(description="Description")
    title_spec: dict[str, str] = Field(description="Title specification")


class UnifiedEstatRecord(BaseModel):
    """Unified record model that can handle all possible estat data structures."""

    # Value columns - these are dynamic but common ones
    tab: str | None = Field(None, description="Table code")
    cat01: str | None = Field(None, description="Category 01 code")
    cat02: str | None = Field(None, description="Category 02 code")
    cat03: str | None = Field(None, description="Category 03 code")
    cat04: str | None = Field(None, description="Category 04 code")
    cat05: str | None = Field(None, description="Category 05 code")
    cat06: str | None = Field(None, description="Category 06 code")
    cat07: str | None = Field(None, description="Category 07 code")
    cat08: str | None = Field(None, description="Category 08 code")
    cat09: str | None = Field(None, description="Category 09 code")
    cat10: str | None = Field(None, description="Category 10 code")
    cat11: str | None = Field(None, description="Category 11 code")
    cat12: str | None = Field(None, description="Category 12 code")
    cat13: str | None = Field(None, description="Category 13 code")
    cat14: str | None = Field(None, description="Category 14 code")
    cat15: str | None = Field(None, description="Category 15 code")
    area: str | None = Field(None, description="Area code")
    time: str | None = Field(None, description="Time code")
    unit: str | None = Field(None, description="Unit")
    value: float | None = Field(None, description="Statistical value")

    # Metadata columns - unified structure
    tab_metadata: UnifiedTabMetadata | None = Field(None, description="Table metadata")
    cat01_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 01 metadata"
    )
    cat02_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 02 metadata"
    )
    cat03_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 03 metadata"
    )
    cat04_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 04 metadata"
    )
    cat05_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 05 metadata"
    )
    cat06_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 06 metadata"
    )
    cat07_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 07 metadata"
    )
    cat08_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 08 metadata"
    )
    cat09_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 09 metadata"
    )
    cat10_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 10 metadata"
    )
    cat11_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 11 metadata"
    )
    cat12_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 12 metadata"
    )
    cat13_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 13 metadata"
    )
    cat14_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 14 metadata"
    )
    cat15_metadata: UnifiedCategoryMetadata | None = Field(
        None, description="Category 15 metadata"
    )
    area_metadata: UnifiedAreaMetadata | None = Field(None, description="Area metadata")
    time_metadata: UnifiedTimeMetadata | None = Field(None, description="Time metadata")

    # Statistical information
    stat_inf: UnifiedStatInf = Field(description="Statistical information")

    # Dynamic fields for unknown columns
    extra_dimensions: dict[str, str | None] = Field(
        default_factory=dict, description="Additional dimension columns"
    )
    extra_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata columns"
    )

    class Config:
        """Pydantic configuration."""

        extra = "allow"  # Allow additional fields
        validate_assignment = True
