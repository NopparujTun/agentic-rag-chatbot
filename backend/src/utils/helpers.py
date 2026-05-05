"""Shared text-processing and formatting utilities.

Functions here are pure (no side effects) and safe to call from any module.
"""

import re


def clean_markdown(markdown_text: str) -> str:
    """Remove horizontal-rule markers that break markdown rendering.

    Strips standalone lines of `---`, `===`, or `___` (three or more
    repetitions) which PDF extraction sometimes produces and which
    renders as unwanted `<h1>` or `<h2>` elements.

    Args:
        markdown_text: Raw markdown text to clean.

    Returns:
        Cleaned text with horizontal-rule artefacts removed.
    """
    if not markdown_text:
        return ""

    cleaned_text = re.sub(r"^[-=_]{3,}\s*$", "", markdown_text, flags=re.MULTILINE)
    return cleaned_text.strip()


def format_time(duration_seconds: float) -> str:
    """Format a duration in seconds into a human-readable Thai string.

    Args:
        duration_seconds: Duration in seconds to format.

    Returns:
        A formatted string like "1.23 วินาที" or "< 0.01 วินาที" for very
        small values.
    """
    if duration_seconds < 0.01:
        return "< 0.01 วินาที"
    return f"{duration_seconds:.2f} วินาที"