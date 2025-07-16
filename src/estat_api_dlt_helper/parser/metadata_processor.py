from typing import Dict, List, Set, Tuple

import pyarrow as pa

from ..models import ClassInfModel, ClassObjModel


class MetadataProcessor:
    """Process metadata and generate Arrow schemas in a type-safe manner."""

    def _create_metadata_struct_type(self, class_obj: ClassObjModel) -> pa.DataType:
        """
        Create metadata struct type from CLASS_OBJ.

        Generates a struct type that includes only the attributes that exist
        in the actual data, ensuring schema compatibility.

        Args:
            class_obj: CLASS_OBJ model containing metadata definitions

        Returns:
            pa.DataType: Arrow struct type for the metadata
        """
        # Basic fields that always exist
        fields: List[Tuple[str, pa.DataType]] = [
            ("code", pa.string()),
            ("name", pa.string()),
        ]

        # Collect additional fields from all CLASS entries
        extra_fields: Set[str] = set()

        for cls in class_obj.class_info:
            attrs = cls.attributes

            # Add standard optional fields if they exist
            if attrs.level is not None:
                extra_fields.add("level")
            if attrs.unit is not None:
                extra_fields.add("unit")
            if attrs.parent_code is not None:
                extra_fields.add("parent_code")

            # Add any extra attributes
            extra_fields.update(attrs.extra_attributes.keys())

        # Add extra fields in sorted order for consistency
        for field_name in sorted(extra_fields):
            fields.append((field_name, pa.string()))

        return pa.struct(fields)

    def _create_metadata_mapping(
        self, class_obj: ClassObjModel
    ) -> Dict[str, Dict[str, str]]:
        """
        Create metadata mapping from CLASS_OBJ.

        Creates a mapping from codes to their metadata attributes,
        including only attributes that have values.

        Args:
            class_obj: CLASS_OBJ model containing metadata definitions

        Returns:
            Dict mapping codes to their metadata dictionaries
        """
        mapping: Dict[str, Dict[str, str]] = {}

        for cls in class_obj.class_info:
            attrs = cls.attributes

            # Start with required fields
            metadata: Dict[str, str] = {
                "code": attrs.code,
                "name": attrs.name,
            }

            # Add optional standard fields if they exist
            if attrs.level is not None:
                metadata["level"] = attrs.level
            if attrs.unit is not None:
                metadata["unit"] = attrs.unit
            if attrs.parent_code is not None:
                metadata["parent_code"] = attrs.parent_code

            # Add extra attributes
            metadata.update(attrs.extra_attributes)

            mapping[attrs.code] = metadata

        return mapping

    def process_metadata(
        self, class_inf: ClassInfModel
    ) -> Tuple[Dict[str, pa.DataType], Dict[str, Dict[str, Dict[str, str]]]]:
        """
        Process metadata to generate Arrow schema types and mappings.

        Args:
            class_inf: CLASS_INF model containing all metadata definitions

        Returns:
            Tuple of:
            - Dict mapping field names to their Arrow struct types
            - Dict mapping field names to their code-to-metadata mappings
        """
        struct_types: Dict[str, pa.DataType] = {}
        mappings: Dict[str, Dict[str, Dict[str, str]]] = {}

        for class_obj in class_inf.class_obj:
            field_name = class_obj.id
            struct_types[field_name] = self._create_metadata_struct_type(class_obj)
            mappings[field_name] = self._create_metadata_mapping(class_obj)

        return struct_types, mappings

    def create_arrow_schema(
        self,
        value_columns: List[str],
        struct_types: Dict[str, pa.DataType],
        stat_inf_type: pa.DataType,
    ) -> pa.Schema:
        """
        Create complete Arrow schema for the table.

        Args:
            value_columns: List of value column names
            struct_types: Dict of metadata struct types
            stat_inf_type: Struct type for table information

        Returns:
            pa.Schema: Complete Arrow schema for the table
        """
        # Start with value columns
        fields: List[Tuple[str, pa.DataType]] = [
            (col, pa.string()) for col in value_columns if col != "value"
        ]

        # Add numeric value column
        fields.append(("value", pa.float64()))

        # Add metadata struct fields
        for field_name, struct_type in struct_types.items():
            fields.append((f"{field_name}_metadata", struct_type))

        # Add table information field
        fields.append(("stat_inf", stat_inf_type))

        return pa.schema(fields)
