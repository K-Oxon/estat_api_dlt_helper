from typing import Any, Dict, Type, Union, get_args, get_origin

import pyarrow as pa
from pydantic import BaseModel


def create_arrow_struct_type(model_class: Type[BaseModel]) -> pa.DataType:
    """Create Arrow struct type from Pydantic model in a type-safe manner."""
    fields: list[tuple[str, pa.DataType]] = []

    for field_name, field_info in model_class.model_fields.items():
        field_type = field_info.annotation

        # Handle Optional types
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            # Check if it's Optional (Union[T, None])
            if type(None) in args:
                # Get the non-None type
                field_type = next(arg for arg in args if arg is not type(None))

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

    for field_name, value in model.model_dump().items():
        if isinstance(value, BaseModel):
            result[field_name] = model_to_arrow_dict(value)
        elif isinstance(value, dict) and any(
            isinstance(v, BaseModel) for v in value.values()
        ):
            # Handle dict with BaseModel values
            result[field_name] = {
                k: model_to_arrow_dict(v) if isinstance(v, BaseModel) else v
                for k, v in value.items()
            }
        else:
            result[field_name] = value

    return result
