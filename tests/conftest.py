"""Test configuration and fixtures."""

import os
import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "live: marks tests as requiring live API access (deselect with '-m \"not live\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Skip live tests if credentials not available."""
    if not (
        os.environ.get("GSLIDES_TEST_DECK_ID")
        and (
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            or os.path.exists("service_account.json")
        )
    ):
        skip_live = pytest.mark.skip(reason="No credentials or test deck ID configured")
        for item in items:
            if "live" in item.keywords:
                item.add_marker(skip_live)