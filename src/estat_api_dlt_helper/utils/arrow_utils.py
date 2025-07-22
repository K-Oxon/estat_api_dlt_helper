import types
from typing import Any, Dict, Type, Union, get_args, get_origin

import pyarrow as pa
from pydantic import BaseModel


def create_arrow_struct_type(model_class: Type[BaseModel]) -> pa.DataType:
    """Create Arrow struct type from Pydantic model in a type-safe manner."""
    fields: list[tuple[str, pa.DataType]] = []

    for field_name, field_info in model_class.model_fields.items():
        field_type = field_info.annotation

        # Handle Optional and Union types
        origin = get_origin(field_type)
        if origin is Union or isinstance(field_type, types.UnionType):
            args = get_args(field_type)
            # Check if it's Optional (Union[T, None])
            if type(None) in args:
                # Get the non-None type
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    field_type = non_none_args[0]
                else:
                    # Multiple non-None types, treat as string
                    field_type = str
            else:
                # Union of multiple non-None types (e.g., int | str)
                # For arrow, we'll use string as the most general type
                field_type = str

        # Map Python types to Arrow types
        arrow_type: pa.DataType
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            # Nested model
            arrow_type = create_arrow_struct_type(field_type)
        elif field_type is str:
            arrow_type = pa.string()
        elif field_type is int:
            arrow_type = pa.int64()
        elif field_type is float:
            arrow_type = pa.float64()
        elif field_type is bool:
            arrow_type = pa.bool_()
        else:
            # Default to string for unknown types
            arrow_type = pa.string()

        fields.append((field_name, arrow_type))

    return pa.struct(fields)


def model_to_arrow_dict(model: BaseModel) -> Dict[str, Any]:
    """Convert Pydantic model to Arrow-compatible dictionary."""
    result: Dict[str, Any] = {}

    for field_name, field_info in model.__class__.model_fields.items():
        # Get the actual value from the model
        value = getattr(model, field_name)

        # Check field type
        field_type = field_info.annotation
        origin = get_origin(field_type)

        # Check if it's a Union type that needs string conversion
        needs_string_conversion = False
        if origin is Union or isinstance(field_type, types.UnionType):
            args = get_args(field_type)
            # If it's a union of non-None types (e.g., int | str), we need string
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) > 1:
                needs_string_conversion = True

        # Process the value
        if value is None:
            processed_value = None
        elif needs_string_conversion:
            # For Union types that need string conversion, convert everything to string
            if isinstance(value, BaseModel):
                # Convert model to dict first, then to string
                processed_value = str(value.model_dump())
            else:
                processed_value = str(value)
        elif isinstance(value, BaseModel):
            processed_value = model_to_arrow_dict(value)
        elif isinstance(value, dict) and any(
            isinstance(v, BaseModel) for v in value.values()
        ):
            # Handle dict with BaseModel values
            processed_value = {
                k: model_to_arrow_dict(v) if isinstance(v, BaseModel) else v
                for k, v in value.items()
            }
        else:
            processed_value = value

        result[field_name] = processed_value

    return result
