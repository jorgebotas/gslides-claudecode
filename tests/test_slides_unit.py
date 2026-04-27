"""Unit tests for slide creation (mocked API calls)."""

from unittest.mock import MagicMock, Mock
import uuid

import pytest

from gslides_claudecode.slides import SlideBuilder


@pytest.fixture
def mock_services():
    """Create mock Google API services."""
    slides_service = MagicMock()
    drive_service = MagicMock()
    return slides_service, drive_service


@pytest.fixture
def slide_builder(mock_services):
    """Create SlideBuilder with mock services."""
    slides_service, drive_service = mock_services
    return SlideBuilder(slides_service, drive_service)


def test_append_text_request_structure(slide_builder, mock_services):
    """Test that append_text generates correct batchUpdate requests."""
    slides_service, _ = mock_services

    # Mock the batchUpdate response
    slides_service.presentations().batchUpdate().execute.return_value = {}

    slide_id = slide_builder.append_text("test_id", "Test Title", "Test Body")

    # Verify batchUpdate was called
    assert slides_service.presentations().batchUpdate.called

    # Get the call arguments
    call_args = slides_service.presentations().batchUpdate.call_args
    presentation_id = call_args[1]["presentationId"]
    requests = call_args[1]["body"]["requests"]

    assert presentation_id == "test_id"
    assert len(requests) == 3

    # Verify createSlide request
    create_request = requests[0]
    assert "createSlide" in create_request
    assert create_request["createSlide"]["slideLayoutReference"]["predefinedLayout"] == "TITLE_AND_BODY"

    # Verify insertText requests
    title_request = requests[1]
    body_request = requests[2]
    assert title_request["insertText"]["text"] == "Test Title"
    assert body_request["insertText"]["text"] == "Test Body"

    assert slide_id.startswith("slide_")


def test_append_bullets_request_structure(slide_builder, mock_services):
    """Test that append_bullets generates correct batchUpdate requests."""
    slides_service, _ = mock_services
    slides_service.presentations().batchUpdate().execute.return_value = {}

    bullets = ["First point", "Second point", "Third point"]
    slide_builder.append_bullets("test_id", "Test Title", bullets)

    call_args = slides_service.presentations().batchUpdate.call_args
    requests = call_args[1]["body"]["requests"]

    assert len(requests) == 4  # createSlide, insertText (title), insertText (body), createParagraphBullets

    # Check bullet formatting request
    bullet_request = requests[3]
    assert "createParagraphBullets" in bullet_request
    assert bullet_request["createParagraphBullets"]["bulletPreset"] == "BULLET_DISC_CIRCLE_SQUARE"

    # Check body text is newline-separated
    body_request = requests[2]
    assert body_request["insertText"]["text"] == "First point\nSecond point\nThird point"


def test_append_image_with_url(slide_builder, mock_services):
    """Test append_image with public URL."""
    slides_service, _ = mock_services
    slides_service.presentations().batchUpdate().execute.return_value = {}

    image_url = "https://example.com/image.png"
    slide_builder.append_image("test_id", "Test Title", image_url=image_url)

    call_args = slides_service.presentations().batchUpdate.call_args
    requests = call_args[1]["body"]["requests"]

    # Find createImage request
    image_request = None
    for req in requests:
        if "createImage" in req:
            image_request = req
            break

    assert image_request is not None
    assert image_request["createImage"]["url"] == image_url


def test_append_image_missing_drive_service():
    """Test error when trying to upload local file without Drive service."""
    slides_service = MagicMock()
    builder = SlideBuilder(slides_service, drive_service=None)

    with pytest.raises(RuntimeError, match="Drive service required"):
        builder.append_image("test_id", "Title", image_path="/path/to/image.jpg")


def test_append_table_request_structure(slide_builder, mock_services):
    """Test that append_table generates correct requests."""
    slides_service, _ = mock_services
    slides_service.presentations().batchUpdate().execute.return_value = {}

    rows = [["Header 1", "Header 2"], ["Value 1", "Value 2"], ["Value 3", "Value 4"]]
    slide_builder.append_table("test_id", "Test Title", rows)

    call_args = slides_service.presentations().batchUpdate.call_args
    requests = call_args[1]["body"]["requests"]

    # Should have: createSlide, insertText (title), createTable, insertText per cell
    expected_requests = 3 + (3 * 2)  # 3 rows × 2 cols
    assert len(requests) == expected_requests

    # Find createTable request
    table_request = None
    for req in requests:
        if "createTable" in req:
            table_request = req
            break

    assert table_request is not None
    assert table_request["createTable"]["rows"] == 3
    assert table_request["createTable"]["columns"] == 2


def test_append_table_empty_rows(slide_builder):
    """Test error with empty rows."""
    with pytest.raises(ValueError, match="At least one row required"):
        slide_builder.append_table("test_id", "Title", [])


def test_append_table_inconsistent_columns(slide_builder):
    """Test error with inconsistent column counts."""
    rows = [["A", "B"], ["C", "D", "E"]]  # Different column counts
    with pytest.raises(ValueError, match="same number of columns"):
        slide_builder.append_table("test_id", "Title", rows)