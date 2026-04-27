"""Unit tests for Deck class wrapper methods."""

from unittest.mock import MagicMock, Mock, patch
import pytest

from gslides_claudecode.deck import Deck


@pytest.fixture
def mock_services():
    """Create mock Google API services."""
    slides_service = MagicMock()
    drive_service = MagicMock()
    return slides_service, drive_service


@pytest.fixture
def deck(mock_services):
    """Create Deck instance with mock services."""
    slides_service, drive_service = mock_services
    return Deck("test_presentation_id", slides_service, drive_service)


def test_deck_initialization(mock_services):
    """Test Deck initialization with services."""
    slides_service, drive_service = mock_services
    presentation_id = "test_presentation_id"

    deck = Deck(presentation_id, slides_service, drive_service)

    assert deck.presentation_id == presentation_id
    assert deck.slides_service == slides_service
    assert deck.drive_service == drive_service
    assert deck.builder is not None


def test_info_method(deck, mock_services):
    """Test info method returns presentation metadata."""
    slides_service, _ = mock_services

    # Mock the API response
    mock_presentation = {
        "title": "Test Presentation",
        "slides": [{"slide1": {}}, {"slide2": {}}, {"slide3": {}}]
    }
    slides_service.presentations().get.return_value.execute.return_value = mock_presentation

    info = deck.info()

    # Verify API call
    slides_service.presentations().get.assert_called_with(
        presentationId="test_presentation_id"
    )

    # Verify returned data
    assert info["title"] == "Test Presentation"
    assert info["slide_count"] == 3
    assert info["presentation_id"] == "test_presentation_id"


def test_info_method_no_title(deck, mock_services):
    """Test info method handles missing title gracefully."""
    slides_service, _ = mock_services

    # Mock presentation without title
    mock_presentation = {"slides": [{"slide1": {}}]}
    slides_service.presentations().get.return_value.execute.return_value = mock_presentation

    info = deck.info()

    assert info["title"] == "Untitled"
    assert info["slide_count"] == 1


def test_info_method_no_slides(deck, mock_services):
    """Test info method handles missing slides gracefully."""
    slides_service, _ = mock_services

    # Mock presentation without slides
    mock_presentation = {"title": "Empty Presentation"}
    slides_service.presentations().get.return_value.execute.return_value = mock_presentation

    info = deck.info()

    assert info["slide_count"] == 0


def test_append_text_delegates_to_builder(deck):
    """Test append_text delegates to SlideBuilder."""
    with patch.object(deck.builder, 'append_text', return_value='slide_123') as mock_append:
        result = deck.append_text("Title", "Body", "Notes")

        mock_append.assert_called_once_with(
            "test_presentation_id", "Title", "Body", "Notes"
        )
        assert result == "slide_123"


def test_append_bullets_delegates_to_builder(deck):
    """Test append_bullets delegates to SlideBuilder."""
    bullets = ["Point 1", "Point 2"]
    with patch.object(deck.builder, 'append_bullets', return_value='slide_456') as mock_append:
        result = deck.append_bullets("Title", bullets, "Notes")

        mock_append.assert_called_once_with(
            "test_presentation_id", "Title", bullets, "Notes"
        )
        assert result == "slide_456"


def test_append_image_delegates_to_builder(deck):
    """Test append_image delegates to SlideBuilder."""
    with patch.object(deck.builder, 'append_image', return_value='slide_789') as mock_append:
        result = deck.append_image("Title", image_url="http://example.com/img.jpg", speaker_notes="Notes")

        mock_append.assert_called_once_with(
            "test_presentation_id", "Title", "http://example.com/img.jpg", None, "Notes"
        )
        assert result == "slide_789"


def test_append_table_delegates_to_builder(deck):
    """Test append_table delegates to SlideBuilder."""
    rows = [["A", "B"], ["1", "2"]]
    with patch.object(deck.builder, 'append_table', return_value='slide_101') as mock_append:
        result = deck.append_table("Title", rows, "Notes")

        mock_append.assert_called_once_with(
            "test_presentation_id", "Title", rows, "Notes"
        )
        assert result == "slide_101"


@patch('gslides_claudecode.deck.load_credentials')
@patch('gslides_claudecode.deck.build_slides_service')
@patch('gslides_claudecode.deck.build_drive_service')
def test_from_service_account_method(mock_build_drive, mock_build_slides, mock_load_creds):
    """Test from_service_account class method."""
    # Mock the dependencies
    mock_creds = Mock()
    mock_slides_service = Mock()
    mock_drive_service = Mock()

    mock_load_creds.return_value = mock_creds
    mock_build_slides.return_value = mock_slides_service
    mock_build_drive.return_value = mock_drive_service

    # Call the method
    deck = Deck.from_service_account("key_file.json", "presentation_id")

    # Verify the calls
    mock_load_creds.assert_called_once_with("key_file.json")
    mock_build_slides.assert_called_once_with(mock_creds)
    mock_build_drive.assert_called_once_with(mock_creds)

    # Verify the result
    assert deck.presentation_id == "presentation_id"
    assert deck.slides_service == mock_slides_service
    assert deck.drive_service == mock_drive_service


def test_deck_with_no_drive_service(mock_services):
    """Test Deck can be created without drive service."""
    slides_service, _ = mock_services

    deck = Deck("test_id", slides_service, drive_service=None)

    assert deck.drive_service is None
    assert deck.builder.drive is None  # SlideBuilder should also have None