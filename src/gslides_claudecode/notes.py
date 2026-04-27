"""Speaker notes utilities for Google Slides."""

from typing import Optional


def set_speaker_notes(slides_service, presentation_id: str, slide_id: str, notes: str) -> None:
    """Add speaker notes to a slide.

    Args:
        slides_service: Google Slides API service client
        presentation_id: ID of the presentation
        slide_id: ID of the slide to add notes to
        notes: Text to add as speaker notes
    """
    if not notes.strip():
        return

    # Get slide metadata to find the speaker notes object ID
    slide = (
        slides_service.presentations()
        .pages()
        .get(presentationId=presentation_id, pageObjectId=slide_id)
        .execute()
    )

    # Extract speaker notes object ID
    notes_properties = slide["slideProperties"]["notesPage"]["notesProperties"]
    speaker_notes_id = notes_properties["speakerNotesObjectId"]

    # Insert text into speaker notes
    requests = [{"insertText": {"objectId": speaker_notes_id, "text": notes}}]

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id, body={"requests": requests}
    ).execute()