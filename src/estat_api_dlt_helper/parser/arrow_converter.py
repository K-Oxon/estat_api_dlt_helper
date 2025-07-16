from typing import Any, Dict, List, Optional

import pyarrow as pa

from ..models import ClassInfModel, TableInf
from ..utils import create_arrow_struct_type, model_to_arrow_dict
from .metadata_processor import MetadataProcessor


class ArrowConverter:
    """Convert JSON data to Arrow format in a type-safe manner."""

    def __init__(self, metadata_processor: MetadataProcessor):
        """
        Initialize converter with metadata processor.

        Args:
            metadata_processor: Processor for handling metadata operations
        """
        self.metadata_processor = metadata_processor

    def _extract_value_columns(self, values: List[Dict[str, Any]]) -> List[str]:
        """
        Extract column names from value data.

        Args:
            values: List of value dictionaries from DATA_INF.VALUE

        Returns:
            List of column names including transformed names
        """
        if not values:
            return []

        # Get first value as sample
        sample = values[0]

        # Extract @ prefixed keys and remove the prefix
        columns = [key.lstrip("@") for key in sample.keys() if key.startswith("@")]

        # Add value column for the $ field
        columns.append("value")

        return columns

    def _parse_numeric_value(self, value: Optional[str]) -> Optional[float]:
        """
        Parse numeric value from string safely.

        Args:
            value: String value to parse

        Returns:
            Parsed float value or None if invalid
        """
        if value is None:
            return None

        # Handle empty strings
        if not value:
            return None

        # Try to parse as float
        try:
            # Remove commas if present (common in Japanese number formatting)
            cleaned_value = value.replace(",", "")
            return float(cleaned_value)
        except (ValueError, AttributeError):
            return None

    def convert_to_arrow(self, stat_data: Dict[str, Any]) -> pa.Table:
        """
        Convert statistical data to Arrow Table.

        Args:
            stat_data: STATISTICAL_DATA section from the API response

        Returns:
            pa.Table: Converted Arrow table with data and metadata
        """
        # Parse and validate metadata
        class_inf = ClassInfModel.model_validate(stat_data["CLASS_INF"])
        struct_types, mappings = self.metadata_processor.process_metadata(class_inf)

        # Extract value data
        values = stat_data["DATA_INF"]["VALUE"]
        value_columns = self._extract_value_columns(values)

        # Prepare data dictionary for Arrow table
        data_dict: Dict[str, pa.Array] = {}

        # Process TABLE_INF (table information)
        table_inf = TableInf.model_validate(stat_data["TABLE_INF"])
        stat_inf_type = create_arrow_struct_type(TableInf)
        stat_inf_data = model_to_arrow_dict(table_inf)

        # Create array with same table info for all rows
        data_dict["stat_inf"] = pa.array(
            [stat_inf_data] * len(values), type=stat_inf_type
        )

        # Handle empty data case
        if not values:
            # Create empty arrays for minimal schema
            if not value_columns:
                value_columns = ["value"]  # At minimum, we need a value column
            for col in value_columns:
                if col == "value":
                    data_dict[col] = pa.array([], type=pa.float64())
                else:
                    data_dict[col] = pa.array([], type=pa.string())
        else:
            # Process value columns normally
            for col in value_columns:
                if col == "value":
                    # Handle numeric value column ($ field)
                    numeric_values = [self._parse_numeric_value(v.get("$")) for v in values]
                    data_dict[col] = pa.array(numeric_values, type=pa.float64())
                else:
                    # Handle string columns (@ prefixed fields)
                    original_key = f"@{col}"
                    string_values = [v.get(original_key, "") for v in values]
                    data_dict[col] = pa.array(string_values, type=pa.string())

        # Add metadata structures
        for field_name, struct_type in struct_types.items():
            original_field = f"@{field_name}"

            # Build metadata array for each row
            metadata_array = []
            for v in values:
                code = v.get(original_field, "")
                # Get metadata for this code
                if code in mappings[field_name]:
                    metadata = mappings[field_name][code]
                else:
                    # Create empty metadata with None values for all fields
                    metadata = {field.name: None for field in struct_type}
                metadata_array.append(metadata)

            data_dict[f"{field_name}_metadata"] = pa.array(
                metadata_array, type=struct_type
            )

        # Create schema and build table
        schema = self.metadata_processor.create_arrow_schema(
            value_columns, struct_types, stat_inf_type
        )

        return pa.Table.from_pydict(data_dict, schema=schema)
