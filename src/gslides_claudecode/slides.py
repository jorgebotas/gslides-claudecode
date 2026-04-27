"""Slide creation utilities for Google Slides."""

import uuid
from pathlib import Path
from typing import List, Optional, Union

from googleapiclient.http import MediaFileUpload

from .notes import set_speaker_notes


class SlideBuilder:
    """Helper class for building different types of slides."""

    def __init__(self, slides_service, drive_service=None):
        self.slides = slides_service
        self.drive = drive_service

    def append_text(
        self,
        presentation_id: str,
        title: str,
        body: str,
        speaker_notes: Optional[str] = None,
    ) -> str:
        """Append a text slide to presentation.

        Args:
            presentation_id: ID of the presentation
            title: Slide title
            body: Main text content
            speaker_notes: Optional speaker notes text

        Returns:
            ID of the created slide
        """
        slide_id = f"slide_{uuid.uuid4().hex[:12]}"
        title_id = f"title_{uuid.uuid4().hex[:12]}"
        body_id = f"body_{uuid.uuid4().hex[:12]}"

        requests = [
            {
                "createSlide": {
                    "objectId": slide_id,
                    "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
                    "placeholderIdMappings": [
                        {"layoutPlaceholder": {"type": "TITLE", "index": 0}, "objectId": title_id},
                        {"layoutPlaceholder": {"type": "BODY", "index": 0}, "objectId": body_id},
                    ],
                }
            },
            {"insertText": {"objectId": title_id, "text": title}},
            {"insertText": {"objectId": body_id, "text": body}},
        ]

        self.slides.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": requests}
        ).execute()

        if speaker_notes:
            set_speaker_notes(self.slides, presentation_id, slide_id, speaker_notes)

        return slide_id

    def append_bullets(
        self,
        presentation_id: str,
        title: str,
        bullets: List[str],
        speaker_notes: Optional[str] = None,
    ) -> str:
        """Append a bulleted list slide to presentation.

        Args:
            presentation_id: ID of the presentation
            title: Slide title
            bullets: List of bullet point texts
            speaker_notes: Optional speaker notes text

        Returns:
            ID of the created slide
        """
        slide_id = f"slide_{uuid.uuid4().hex[:12]}"
        title_id = f"title_{uuid.uuid4().hex[:12]}"
        body_id = f"body_{uuid.uuid4().hex[:12]}"

        # Create slide with title and body
        requests = [
            {
                "createSlide": {
                    "objectId": slide_id,
                    "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
                    "placeholderIdMappings": [
                        {"layoutPlaceholder": {"type": "TITLE", "index": 0}, "objectId": title_id},
                        {"layoutPlaceholder": {"type": "BODY", "index": 0}, "objectId": body_id},
                    ],
                }
            },
            {"insertText": {"objectId": title_id, "text": title}},
            {"insertText": {"objectId": body_id, "text": "\n".join(bullets)}},
            {
                "createParagraphBullets": {
                    "objectId": body_id,
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                }
            },
        ]

        self.slides.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": requests}
        ).execute()

        if speaker_notes:
            set_speaker_notes(self.slides, presentation_id, slide_id, speaker_notes)

        return slide_id

    def append_image(
        self,
        presentation_id: str,
        title: str,
        image_url: Optional[str] = None,
        image_path: Optional[Union[str, Path]] = None,
        speaker_notes: Optional[str] = None,
    ) -> str:
        """Append an image slide to presentation.

        Args:
            presentation_id: ID of the presentation
            title: Slide title
            image_url: Public URL of image (mutually exclusive with image_path)
            image_path: Local file path to upload (mutually exclusive with image_url)
            speaker_notes: Optional speaker notes text

        Returns:
            ID of the created slide

        Raises:
            ValueError: If neither or both image_url and image_path provided
            RuntimeError: If image_path provided but no Drive service available
        """
        if not bool(image_url) ^ bool(image_path):
            raise ValueError("Provide exactly one of image_url or image_path")

        if image_path and not self.drive:
            raise RuntimeError("Drive service required for local file uploads")

        slide_id = f"slide_{uuid.uuid4().hex[:12]}"
        title_id = f"title_{uuid.uuid4().hex[:12]}"

        # Upload local file to Drive if needed
        if image_path:
            image_url = self._upload_image_to_drive(image_path)

        requests = [
            {
                "createSlide": {
                    "objectId": slide_id,
                    "slideLayoutReference": {"predefinedLayout": "TITLE_ONLY"},
                    "placeholderIdMappings": [
                        {"layoutPlaceholder": {"type": "TITLE", "index": 0}, "objectId": title_id},
                    ],
                }
            },
            {"insertText": {"objectId": title_id, "text": title}},
            {
                "createImage": {
                    "objectId": f"image_{uuid.uuid4().hex[:12]}",
                    "url": image_url,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"height": {"magnitude": 3000000, "unit": "EMU"},
                                "width": {"magnitude": 4000000, "unit": "EMU"}},
                        "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 1500000,
                            "translateY": 1500000,
                            "unit": "EMU"
                        }
                    },
                }
            },
        ]

        self.slides.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": requests}
        ).execute()

        if speaker_notes:
            set_speaker_notes(self.slides, presentation_id, slide_id, speaker_notes)

        return slide_id

    def append_table(
        self,
        presentation_id: str,
        title: str,
        rows: List[List[str]],
        speaker_notes: Optional[str] = None,
    ) -> str:
        """Append a table slide to presentation.

        Args:
            presentation_id: ID of the presentation
            title: Slide title
            rows: List of rows, where each row is a list of cell values
            speaker_notes: Optional speaker notes text

        Returns:
            ID of the created slide

        Raises:
            ValueError: If rows is empty or rows have inconsistent lengths
        """
        if not rows:
            raise ValueError("At least one row required")

        num_cols = len(rows[0])
        if not all(len(row) == num_cols for row in rows):
            raise ValueError("All rows must have the same number of columns")

        slide_id = f"slide_{uuid.uuid4().hex[:12]}"
        title_id = f"title_{uuid.uuid4().hex[:12]}"
        table_id = f"table_{uuid.uuid4().hex[:12]}"

        # Create slide with title and table
        requests = [
            {
                "createSlide": {
                    "objectId": slide_id,
                    "slideLayoutReference": {"predefinedLayout": "TITLE_ONLY"},
                    "placeholderIdMappings": [
                        {"layoutPlaceholder": {"type": "TITLE", "index": 0}, "objectId": title_id},
                    ],
                }
            },
            {"insertText": {"objectId": title_id, "text": title}},
            {
                "createTable": {
                    "objectId": table_id,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"height": {"magnitude": 3000000, "unit": "EMU"},
                                "width": {"magnitude": 8000000, "unit": "EMU"}},
                        "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 500000,
                            "translateY": 1500000,
                            "unit": "EMU"
                        }
                    },
                    "rows": len(rows),
                    "columns": num_cols,
                }
            },
        ]

        # Add text to table cells
        for row_idx, row in enumerate(rows):
            for col_idx, cell_text in enumerate(row):
                requests.append({
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": row_idx, "columnIndex": col_idx},
                        "text": cell_text,
                    }
                })

        self.slides.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": requests}
        ).execute()

        if speaker_notes:
            set_speaker_notes(self.slides, presentation_id, slide_id, speaker_notes)

        return slide_id

    def _upload_image_to_drive(self, image_path: Union[str, Path]) -> str:
        """Upload local image to Drive and return public URL."""
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Upload file to Drive
        media = MediaFileUpload(str(image_path), resumable=True)
        file_metadata = {"name": image_path.name}

        file = (
            self.drive.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        file_id = file.get("id")

        # Make file publicly readable
        self.drive.permissions().create(
            fileId=file_id, body={"role": "reader", "type": "anyone"}
        ).execute()

        # Return public Drive URL
        return f"https://drive.google.com/uc?id={file_id}"