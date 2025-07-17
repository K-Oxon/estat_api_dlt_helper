"""Configuration models for estat_api_dlt_helper."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceConfig(BaseModel):
    """e-Stat API source configuration."""

    app_id: str = Field(..., description="e-Stat API application ID (API key)")
    statsDataId: Union[str, List[str]] = Field(
        ...,
        description="Statistical table ID(s) to fetch. Can be a single ID or list of IDs",
    )
    lang: Literal["J", "E"] = Field("J", description="Language of the API response")
    metaGetFlg: Literal["Y", "N"] = Field(
        "Y", description="Whether to fetch metadata (Y/N)"
    )
    cntGetFlg: Literal["Y", "N"] = Field(
        "N", description="Whether to fetch only count (Y/N)"
    )

    # 以下オプションパラメータ
    explanationGetFlg: Optional[Literal["Y", "N"]] = Field(
        "Y", description="Whether to fetch explanations (Y/N)"
    )
    annotationGetFlg: Optional[Literal["Y", "N"]] = Field(
        "Y", description="Whether to fetch annotations (Y/N)"
    )
    replaceSpChars: Literal["0", "1", "2", "3"] = Field(
        "2",
        description="Special character replacement mode | 0: 置換しない, 1: 置換する, 2: NULL, 3: 'NA'",
    )

    # データ選択パラメータ
    lvTab: Optional[str] = Field(None, description="Table level")
    cdTab: Optional[str] = Field(None, description="Table code")
    cdTabFrom: Optional[str] = Field(None, description="Table code from")
    cdTabTo: Optional[str] = Field(None, description="Table code to")
    lvTime: Optional[str] = Field(None, description="Time level")
    cdTime: Optional[str] = Field(None, description="Time code")
    cdTimeFrom: Optional[str] = Field(None, description="Time code from")
    cdTimeTo: Optional[str] = Field(None, description="Time code to")
    lvArea: Optional[str] = Field(None, description="Area level")
    cdArea: Optional[str] = Field(None, description="Area code")
    cdAreaFrom: Optional[str] = Field(None, description="Area code from")
    cdAreaTo: Optional[str] = Field(None, description="Area code to")
    # ... see https://api.e-stat.go.jp/swagger-ui/e-statapi3.0.html#/

    # ページネーションパラメータ
    limit: int = Field(
        100000, description="Maximum number of records to fetch per request"
    )
    maximum_offset: Optional[int] = Field(
        None, description="Maximum number of records to fetch"
    )

    # 分類事項パラメータ（cat01-cat15）
    # 動的に生成されるため、Extraで受け入れる
    model_config = ConfigDict(extra="allow")

    @field_validator("statsDataId")
    @classmethod
    def validate_stats_data_id(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """Ensure statsDataId is valid."""
        if isinstance(v, list):
            if not v:
                raise ValueError("statsDataId list cannot be empty")
            for id_ in v:
                if not isinstance(id_, str) or not id_.strip():
                    raise ValueError(f"Invalid statsDataId: {id_}")
        elif isinstance(v, str):
            if not v.strip():
                raise ValueError("statsDataId cannot be empty")
        return v


class DestinationConfig(BaseModel):
    """DLT destination configuration."""

    destination: Union[str, Any] = Field(
        ...,
        description="DLT destination configuration | e.g. 'bigquery', 'duckdb', 'filesystem', 'motherduck'",
    )
    dataset_name: str = Field(..., description="Dataset/schema name in the destination")
    table_name: str = Field(..., description="Table name in the destination")
    write_disposition: Literal["append", "replace", "merge"] = Field(
        "merge", description="How to write data to the destination table"
    )
    primary_key: Optional[Union[str, List[str]]] = Field(
        ["time", "area", "cat01"],
        description="Primary key column(s) for merge operations",
    )

    # DLT pipeline configuration
    pipeline_name: Optional[str] = Field(None, description="Name of the DLT pipeline")
    dev_mode: bool = Field(False, description="Enable DLT development mode")

    # Additional destination-specific configuration
    credentials: Optional[Dict[str, Any]] = Field(
        None, description="Destination-specific credentials"
    )
    extra_options: Optional[Dict[str, Any]] = Field(
        None, description="Additional destination-specific options"
    )

    @field_validator("primary_key")
    @classmethod
    def validate_primary_key(
        cls, v: Optional[Union[str, List[str]]], info
    ) -> Optional[Union[str, List[str]]]:
        """Validate primary key is provided for merge operations."""
        write_disposition = info.data.get("write_disposition")
        if write_disposition == "merge" and not v:
            raise ValueError(
                "primary_key must be specified when write_disposition is 'merge'"
            )
        return v


class EstatDltConfig(BaseModel):
    """Main configuration for e-Stat API to DLT integration."""

    source: SourceConfig = Field(..., description="e-Stat API source configuration")
    destination: DestinationConfig = Field(
        ..., description="DLT destination configuration"
    )

    # Optional processing configuration
    batch_size: Optional[int] = Field(
        None, description="Number of records to process in each batch"
    )
    max_retries: int = Field(3, description="Maximum number of API retry attempts")
    timeout: Optional[int] = Field(None, description="API request timeout in seconds")

    # Data transformation options
    flatten_metadata: bool = Field(
        False, description="Whether to flatten metadata into table columns"
    )
    include_api_metadata: bool = Field(
        True, description="Whether to include API response metadata in the table"
    )

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )
