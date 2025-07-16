from typing import Any, Dict

import pyarrow as pa

from .arrow_converter import ArrowConverter
from .metadata_processor import MetadataProcessor


def parse_response(data: Dict[str, Any]) -> pa.Table:
    """
    Parse e-Stat API response data and convert to Arrow table.

    This is the main entry point for parsing e-Stat API responses.
    Takes the JSON response and returns a structured Arrow table with
    data values and associated metadata.

    Args:
        data: The complete JSON response from e-Stat API

    Returns:
        pa.Table: Arrow table containing the parsed data with metadata

    Raises:
        ValueError: If required data sections are missing
        KeyError: If expected keys are not found in the response
    """
    # Validate response structure
    if "GET_STATS_DATA" not in data:
        raise ValueError("Invalid response: missing GET_STATS_DATA section")

    stats_data = data["GET_STATS_DATA"]

    if "STATISTICAL_DATA" not in stats_data:
        raise ValueError("Invalid response: missing STATISTICAL_DATA section")

    statistical_data = stats_data["STATISTICAL_DATA"]

    # Check for required sections
    required_sections = ["TABLE_INF", "CLASS_INF", "DATA_INF"]
    missing_sections = [
        section for section in required_sections if section not in statistical_data
    ]

    if missing_sections:
        raise ValueError(
            f"Invalid response: missing required sections: {', '.join(missing_sections)}"
        )

    # Validate DATA_INF has VALUE
    if "VALUE" not in statistical_data["DATA_INF"]:
        raise ValueError("Invalid response: DATA_INF missing VALUE section")

    # Create processors
    metadata_processor = MetadataProcessor()
    arrow_converter = ArrowConverter(metadata_processor)

    # Convert to Arrow table
    return arrow_converter.convert_to_arrow(statistical_data)
