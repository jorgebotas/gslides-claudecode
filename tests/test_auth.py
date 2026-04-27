"""Tests for authentication module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gslides_claudecode.auth import SCOPES, load_credentials


def test_scopes_defined():
    """Test that required scopes are defined."""
    assert len(SCOPES) == 2
    assert "https://www.googleapis.com/auth/presentations" in SCOPES
    assert "https://www.googleapis.com/auth/drive.file" in SCOPES


def test_load_credentials_file_not_found():
    """Test error when key file doesn't exist."""
    with pytest.raises(FileNotFoundError, match="Service account key file not found"):
        load_credentials("nonexistent.json")


def test_load_credentials_env_var():
    """Test loading credentials from environment variable."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"type": "service_account", "project_id": "test"}')
        temp_path = f.name

    try:
        with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": temp_path}):
            with patch("gslides_claudecode.auth.service_account.Credentials.from_service_account_file") as mock_creds:
                load_credentials()
                mock_creds.assert_called_once_with(temp_path, scopes=SCOPES)
    finally:
        Path(temp_path).unlink()


def test_load_credentials_default_path():
    """Test loading credentials from default path when no env var set."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("gslides_claudecode.auth.service_account.Credentials.from_service_account_file") as mock_creds:
            with patch("pathlib.Path.exists", return_value=True):
                load_credentials()
                mock_creds.assert_called_once_with("service_account.json", scopes=SCOPES)