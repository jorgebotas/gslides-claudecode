"""Main Deck class for Google Slides API interactions."""

from pathlib import Path
from typing import List, Optional, Union

from .auth import build_drive_service, build_slides_service, load_credentials
from .slides import SlideBuilder


class Deck:
    """Represents a Google Slides presentation."""

    def __init__(self, presentation_id: str, slides_service, drive_service=None):
        """Initialize Deck with API services.

        Args:
            presentation_id: ID of the Google Slides presentation
            slides_service: Google Slides API service client
            drive_service: Optional Google Drive API service client (needed for image uploads)
        """
        self.presentation_id = presentation_id
        self.slides_service = slides_service
        self.drive_service = drive_service
        self.builder = SlideBuilder(slides_service, drive_service)

    @classmethod
    def from_service_account(
        cls, key_file: Optional[str] = None, presentation_id: str = None
    ) -> "Deck":
        """Create Deck from service account credentials.

        Args:
            key_file: Path to service account JSON file. If None, uses default resolution order.
            presentation_id: ID of the presentation to work with

        Returns:
            Deck instance configured with API services
        """
        credentials = load_credentials(key_file)
        slides_service = build_slides_service(credentials)
        drive_service = build_drive_service(credentials)

        return cls(presentation_id, slides_service, drive_service)

    def info(self) -> dict:
        """Get basic information about the presentation.

        Returns:
            Dictionary with title and slide count
        """
        presentation = (
            self.slides_service.presentations()
            .get(presentationId=self.presentation_id)
            .execute()
        )

        return {
            "title": presentation.get("title", "Untitled"),
            "slide_count": len(presentation.get("slides", [])),
            "presentation_id": self.presentation_id,
        }

    def list_slides(self) -> list[dict]:
        """List every slide in the presentation.

        Returns:
            List of dicts with keys ``object_id`` (stable slide id),
            ``index`` (0-based position), ``title`` (text from the first
            TITLE or CENTERED_TITLE placeholder, or "" if none).
        """
        presentation = (
            self.slides_service.presentations()
            .get(presentationId=self.presentation_id)
            .execute()
        )
        out = []
        for i, slide in enumerate(presentation.get("slides", [])):
            title = ""
            for element in slide.get("pageElements", []):
                shape = element.get("shape", {})
                placeholder = shape.get("placeholder", {})
                ptype = placeholder.get("type", "")
                if ptype in ("TITLE", "CENTERED_TITLE"):
                    text_runs = shape.get("text", {}).get("textElements", [])
                    title = "".join(
                        run["textRun"]["content"]
                        for run in text_runs
                        if "textRun" in run
                    ).strip()
                    break
            out.append({
                "object_id": slide["objectId"],
                "index": i,
                "title": title,
            })
        return out

    def delete_slide(self, object_id: str) -> None:
        """Delete a slide by its objectId (see ``list_slides``)."""
        self.slides_service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={"requests": [{"deleteObject": {"objectId": object_id}}]},
        ).execute()

    def move_slide(self, object_id: str, new_index: int) -> None:
        """Move a slide to ``new_index`` (0-based)."""
        self.slides_service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={"requests": [{
                "updateSlidesPosition": {
                    "slideObjectIds": [object_id],
                    "insertionIndex": new_index,
                }
            }]},
        ).execute()

    def append_text(
        self, title: str, body: str, speaker_notes: Optional[str] = None
    ) -> str:
        """Append a text slide to presentation."""
        return self.builder.append_text(
            self.presentation_id, title, body, speaker_notes
        )

    def append_bullets(
        self, title: str, bullets: List[str], speaker_notes: Optional[str] = None
    ) -> str:
        """Append a bulleted list slide to presentation."""
        return self.builder.append_bullets(
            self.presentation_id, title, bullets, speaker_notes
        )

    def append_image(
        self,
        title: str,
        image_url: Optional[str] = None,
        image_path: Optional[Union[str, Path]] = None,
        speaker_notes: Optional[str] = None,
        max_dimension: Optional[int] = 1600,
    ) -> str:
        """Append an image slide to presentation.

        Local images are auto-downscaled to max_dimension px (longest edge)
        before upload to stay under the Slides API's ~2 MB image limit.
        Pass max_dimension=None to disable downscaling.
        """
        return self.builder.append_image(
            self.presentation_id, title, image_url, image_path, speaker_notes,
            max_dimension=max_dimension,
        )

    def append_table(
        self, title: str, rows: List[List[str]], speaker_notes: Optional[str] = None
    ) -> str:
        """Append a table slide to presentation."""
        return self.builder.append_table(
            self.presentation_id, title, rows, speaker_notes
        )

    def append_section_header(
        self,
        title: str,
        subtitle: Optional[str] = None,
        background_color: Optional[str] = "#4285F4",
        text_color: str = "#FFFFFF",
        speaker_notes: Optional[str] = None,
    ) -> str:
        """Append a section divider slide with large centered title.

        Pass background_color=None for no fill. Defaults to Google blue
        (#4285F4) with white text — good for report date dividers.
        """
        return self.builder.append_section_header(
            self.presentation_id, title, subtitle,
            background_color=background_color, text_color=text_color,
            speaker_notes=speaker_notes,
        )