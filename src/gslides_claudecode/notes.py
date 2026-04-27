"""Speaker notes utilities for Google Slides."""


def _existing_notes_length(notes_page: dict, speaker_notes_id: str) -> int:
    for element in notes_page.get("pageElements", []):
        if element.get("objectId") != speaker_notes_id:
            continue
        text = element.get("shape", {}).get("text", {})
        total = 0
        for te in text.get("textElements", []):
            total += len(te.get("textRun", {}).get("content", ""))
        return total
    return 0


def set_speaker_notes(slides_service, presentation_id: str, slide_id: str, notes: str) -> None:
    """Replace the speaker notes on a slide.

    Safe on fresh slides where the notes placeholder is empty — no deleteText
    is issued unless there is existing text (deleteText with an empty range
    fails with "startIndex 0 must be less than endIndex 0").
    """
    if not notes.strip():
        return

    page = (
        slides_service.presentations()
        .pages()
        .get(presentationId=presentation_id, pageObjectId=slide_id)
        .execute()
    )

    notes_page = page["slideProperties"]["notesPage"]
    speaker_notes_id = notes_page["notesProperties"]["speakerNotesObjectId"]

    requests = []
    if _existing_notes_length(notes_page, speaker_notes_id) > 0:
        requests.append(
            {"deleteText": {"objectId": speaker_notes_id, "textRange": {"type": "ALL"}}}
        )
    requests.append({"insertText": {"objectId": speaker_notes_id, "text": notes}})

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id, body={"requests": requests}
    ).execute()
