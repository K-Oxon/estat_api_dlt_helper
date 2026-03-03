"""Shared fixtures and helpers for integration tests."""

import os

import pytest

APP_ID = os.getenv("ESTAT_API_KEY")
SKIP_INTEGRATION = os.getenv("SKIP_INTEGRATION_TESTS", "").lower() == "true"


def skip_if_no_api_key():
    """Skip the module if API key is not set or integration tests are disabled."""
    if not APP_ID or SKIP_INTEGRATION:
        skip_reason = []
        if not APP_ID:
            skip_reason.append("ESTAT_API_KEY environment variable not set")
        if SKIP_INTEGRATION:
            skip_reason.append("SKIP_INTEGRATION_TESTS is set to true")
        pytest.skip(" and ".join(skip_reason), allow_module_level=True)
