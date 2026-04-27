"""Google Slides API wrapper for Claude Code projects."""

from .deck import Deck
from .slides import SlideBuilder

__version__ = "0.1.0"
__all__ = ["Deck", "SlideBuilder"]