"""
Live integration tests for gslides-claudecode

Tests real Google Slides API calls using service account credentials.
Only runs when both GOOGLE_APPLICATION_CREDENTIALS and GSLIDES_TEST_DECK_ID are set.
"""

import os
import pytest
import uuid
from gslides_claudecode import Deck

# Test resources - only run if both env vars are set
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
TEST_DECK_ID = os.getenv("GSLIDES_TEST_DECK_ID")

pytestmark = pytest.mark.skipif(
    not (CREDENTIALS_PATH and TEST_DECK_ID),
    reason="Live tests require GOOGLE_APPLICATION_CREDENTIALS and GSLIDES_TEST_DECK_ID"
)

@pytest.fixture
def deck():
    """Provide authenticated Deck instance for tests."""
    if not (CREDENTIALS_PATH and TEST_DECK_ID):
        pytest.skip("Missing credentials or test deck ID")

    return Deck.from_service_account(key_file=CREDENTIALS_PATH, presentation_id=TEST_DECK_ID)

@pytest.fixture
def cleanup_slides():
    """Track slides created during tests for cleanup."""
    created_slide_ids = []

    def register_slide(slide_id):
        created_slide_ids.append(slide_id)

    yield register_slide

    # Cleanup: delete all created slides
    if created_slide_ids and CREDENTIALS_PATH and TEST_DECK_ID:
        # Use raw batchUpdate to delete slides
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        SCOPES = ["https://www.googleapis.com/auth/presentations"]
        creds = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        slides_service = build("slides", "v1", credentials=creds, cache_discovery=False)

        # Delete slides in reverse order (newest first) to avoid index issues
        for slide_id in reversed(created_slide_ids):
            try:
                request = {"deleteObject": {"objectId": slide_id}}
                slides_service.presentations().batchUpdate(
                    presentationId=TEST_DECK_ID,
                    body={"requests": [request]}
                ).execute()
                print(f"Cleaned up slide: {slide_id}")
            except Exception as e:
                print(f"Warning: Failed to clean up slide {slide_id}: {e}")


class TestLiveIntegration:
    """Live tests that create and clean up actual slides."""

    def test_deck_connection(self, deck):
        """Verify we can connect and read basic deck info."""
        info = deck.info()
        assert isinstance(info["title"], str) and info["title"]
        assert "slide_count" in info
        assert info["presentation_id"] == TEST_DECK_ID

    def test_append_text_slide(self, deck, cleanup_slides):
        """Test creating a text slide with speaker notes."""
        title = f"Test Text {uuid.uuid4().hex[:8]}"
        body = "This is a test text slide body"
        notes = "Test speaker notes for text slide"

        # Capture slide_id from response for cleanup
        slide_id = deck.append_text(title=title, body=body, speaker_notes=notes)
        cleanup_slides(slide_id)

        # Verify slide was created (check deck info)
        info = deck.info()
        assert info["slide_count"] > 0

    def test_append_bullets_slide(self, deck, cleanup_slides):
        """Test creating a bullet point slide."""
        title = f"Test Bullets {uuid.uuid4().hex[:8]}"
        bullets = ["First bullet point", "Second bullet point", "Third bullet point"]
        notes = "Test notes for bullet slide"

        slide_id = deck.append_bullets(title=title, bullets=bullets, speaker_notes=notes)
        cleanup_slides(slide_id)

        # Verify the slide was created
        info = deck.info()
        assert info["slide_count"] > 0

    def test_append_image_slide_url(self, deck, cleanup_slides):
        """Test creating an image slide from public URL."""
        title = f"Test Image {uuid.uuid4().hex[:8]}"
        image_url = "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
        notes = "Test image slide from public URL"

        slide_id = deck.append_image(title=title, image_url=image_url, speaker_notes=notes)
        cleanup_slides(slide_id)

        # Verify the slide was created
        info = deck.info()
        assert info["slide_count"] > 0

    def test_append_table_slide(self, deck, cleanup_slides):
        """Test creating a table slide from CSV data."""
        title = f"Test Table {uuid.uuid4().hex[:8]}"

        # Read test CSV and convert to rows format
        import csv
        with open("/tmp/test_metrics.csv", "r") as f:
            reader = csv.reader(f)
            rows = list(reader)

        notes = "Test table slide from CSV data"

        slide_id = deck.append_table(title=title, rows=rows, speaker_notes=notes)
        cleanup_slides(slide_id)

        # Verify the slide was created
        info = deck.info()
        assert info["slide_count"] > 0