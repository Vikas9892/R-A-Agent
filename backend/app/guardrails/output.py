import re
from typing import Any

MAX_OUTPUT_LENGTH = 4000

# Patterns for accidental internal debug or workflow markers
INTERNAL_LEAK_PATTERNS = [
    re.compile(r"\{\s*\"action\"\s*:\s*\"finish\".*?\}", re.DOTALL),
    re.compile(r"\{\s*\"action\"\s*:\s*\"tool\".*?\}", re.DOTALL),
    re.compile(r"^SYSTEM:\s*", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^USER REQUEST:\s*", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^RESEARCH:\s*", re.IGNORECASE | re.MULTILINE),
]


def validate_output(output_content: Any) -> tuple[bool, str]:
    """Deterministically validate and sanitize the synthesized answer.

    Checks:
    1. Ensures the answer is a valid string.
    2. Rejects empty or whitespace-only answers.
    3. Strips accidental internal workflow/prompt tags.
    4. Truncates output cleanly if it exceeds MAX_OUTPUT_LENGTH.

    Returns:
        (is_valid, sanitized_output): True with sanitized text,
                                     or False with error description.
    """
    if not isinstance(output_content, str):
        return False, "Output must be a string."

    cleaned = output_content.strip()
    if not cleaned:
        return False, "Output cannot be empty."

    # Scrub accidental internal markers
    for pattern in INTERNAL_LEAK_PATTERNS:
        cleaned = pattern.sub("", cleaned).strip()

    if not cleaned:
        return False, "Output was empty after stripping internal debug artifacts."

    if len(cleaned) > MAX_OUTPUT_LENGTH:
        cleaned = cleaned[:MAX_OUTPUT_LENGTH] + "... [truncated]"

    return True, cleaned
