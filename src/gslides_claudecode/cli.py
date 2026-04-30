"""Command-line interface for gslides-claudecode."""

import argparse
import csv
import sys
from pathlib import Path
from typing import List

from .deck import Deck


def cmd_test(args):
    """Test connection to Google Slides API."""
    try:
        deck = Deck.from_service_account(args.key_file, args.presentation_id)
        info = deck.info()
        print(f"✓ Connected successfully!")
        print(f"Title: {info['title']}")
        print(f"Slides: {info['slide_count']}")
        print(f"Presentation ID: {info['presentation_id']}")
    except Exception as e:
        print(f"✗ Connection failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_text(args):
    """Add a text slide."""
    try:
        deck = Deck.from_service_account(args.key_file, args.presentation_id)
        slide_id = deck.append_text(args.title, args.body, args.notes)
        print(f"✓ Added text slide: {slide_id}")
    except Exception as e:
        print(f"✗ Failed to add text slide: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_bullets(args):
    """Add a bulleted list slide."""
    try:
        deck = Deck.from_service_account(args.key_file, args.presentation_id)
        bullets = [bullet.strip() for bullet in args.bullets.split(",")]
        slide_id = deck.append_bullets(args.title, bullets, args.notes)
        print(f"✓ Added bullets slide: {slide_id}")
    except Exception as e:
        print(f"✗ Failed to add bullets slide: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_image(args):
    """Add an image slide."""
    try:
        deck = Deck.from_service_account(args.key_file, args.presentation_id)
        slide_id = deck.append_image(
            args.title,
            image_url=args.url,
            image_path=args.path,
            speaker_notes=args.notes,
        )
        print(f"✓ Added image slide: {slide_id}")
    except Exception as e:
        print(f"✗ Failed to add image slide: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_table(args):
    """Add a table slide from CSV."""
    try:
        # Read CSV data
        csv_path = Path(args.csv)
        if not csv_path.exists():
            print(f"✗ CSV file not found: {csv_path}", file=sys.stderr)
            sys.exit(1)

        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            print("✗ CSV file is empty", file=sys.stderr)
            sys.exit(1)

        deck = Deck.from_service_account(args.key_file, args.presentation_id)
        slide_id = deck.append_table(args.title, rows, args.notes)
        print(f"✓ Added table slide: {slide_id}")
    except Exception as e:
        print(f"✗ Failed to add table slide: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_section(args):
    """Add a section header slide."""
    try:
        deck = Deck.from_service_account(args.key_file, args.presentation_id)
        bg = None if args.no_bg else args.bg_color
        slide_id = deck.append_section_header(
            args.title,
            subtitle=args.subtitle,
            background_color=bg,
            text_color=args.text_color,
            speaker_notes=args.notes,
        )
        print(f"✓ Added section header: {slide_id}")
    except Exception as e:
        print(f"✗ Failed to add section header: {e}", file=sys.stderr)
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="gslides",
        description="Google Slides API command-line interface",
    )

    parser.add_argument(
        "--key-file",
        help="Path to service account JSON file (default: $GOOGLE_APPLICATION_CREDENTIALS or ./service_account.json)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test API connection")
    test_parser.add_argument("presentation_id", help="Google Slides presentation ID")

    # Text command
    text_parser = subparsers.add_parser("text", help="Add text slide")
    text_parser.add_argument("presentation_id", help="Google Slides presentation ID")
    text_parser.add_argument("--title", required=True, help="Slide title")
    text_parser.add_argument("--body", required=True, help="Slide body text")
    text_parser.add_argument("--notes", help="Speaker notes")

    # Bullets command
    bullets_parser = subparsers.add_parser("bullets", help="Add bulleted list slide")
    bullets_parser.add_argument("presentation_id", help="Google Slides presentation ID")
    bullets_parser.add_argument("--title", required=True, help="Slide title")
    bullets_parser.add_argument(
        "--bullets", required=True, help="Comma-separated bullet points"
    )
    bullets_parser.add_argument("--notes", help="Speaker notes")

    # Image command
    image_parser = subparsers.add_parser("image", help="Add image slide")
    image_parser.add_argument("presentation_id", help="Google Slides presentation ID")
    image_parser.add_argument("--title", required=True, help="Slide title")
    image_group = image_parser.add_mutually_exclusive_group(required=True)
    image_group.add_argument("--url", help="Public image URL")
    image_group.add_argument("--path", help="Local image file path")
    image_parser.add_argument("--notes", help="Speaker notes")

    # Table command
    table_parser = subparsers.add_parser("table", help="Add table slide from CSV")
    table_parser.add_argument("presentation_id", help="Google Slides presentation ID")
    table_parser.add_argument("--title", required=True, help="Slide title")
    table_parser.add_argument("--csv", required=True, help="Path to CSV file")
    table_parser.add_argument("--notes", help="Speaker notes")

    # Section header command
    section_parser = subparsers.add_parser(
        "section", help="Add section divider slide with optional colored background"
    )
    section_parser.add_argument("presentation_id", help="Google Slides presentation ID")
    section_parser.add_argument("--title", required=True, help="Section title")
    section_parser.add_argument("--subtitle", help="Optional subtitle (e.g. date)")
    section_parser.add_argument(
        "--bg-color", default="#4285F4",
        help="Background color as #RRGGBB (default #4285F4 Google blue)",
    )
    section_parser.add_argument(
        "--no-bg", action="store_true", help="No background fill (overrides --bg-color)"
    )
    section_parser.add_argument(
        "--text-color", default="#FFFFFF", help="Text color as #RRGGBB (default white)"
    )
    section_parser.add_argument("--notes", help="Speaker notes")

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Dispatch to command handlers
    command_handlers = {
        "test": cmd_test,
        "text": cmd_text,
        "bullets": cmd_bullets,
        "image": cmd_image,
        "table": cmd_table,
        "section": cmd_section,
    }

    handler = command_handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()