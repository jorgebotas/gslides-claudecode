"""Google API authentication utilities."""

import os
from pathlib import Path
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Required OAuth scopes for Google Slides and Drive APIs
SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]


def load_credentials(key_file: Optional[str] = None) -> service_account.Credentials:
    """Load service account credentials from file.

    Args:
        key_file: Path to service account JSON file. If None, tries:
                  1. $GOOGLE_APPLICATION_CREDENTIALS environment variable
                  2. ./service_account.json in current directory

    Returns:
        Authenticated service account credentials

    Raises:
        FileNotFoundError: If no valid key file found
        ValueError: If key file is invalid
    """
    if key_file is None:
        # Try environment variable first
        key_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if key_file is None:
            # Fall back to default location
            key_file = "service_account.json"

    key_path = Path(key_file)
    if not key_path.exists():
        raise FileNotFoundError(f"Service account key file not found: {key_path}")

    try:
        return service_account.Credentials.from_service_account_file(
            str(key_path), scopes=SCOPES
        )
    except Exception as e:
        raise ValueError(f"Invalid service account key file: {e}")


def build_slides_service(credentials: service_account.Credentials):
    """Build Google Slides API service client."""
    return build("slides", "v1", credentials=credentials, cache_discovery=False)


def build_drive_service(credentials: service_account.Credentials):
    """Build Google Drive API service client."""
    return build("drive", "v3", credentials=credentials, cache_discovery=False)