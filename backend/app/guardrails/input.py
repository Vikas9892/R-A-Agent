import re

MAX_INPUT_LENGTH = 1000

# Deterministic patterns matching prompt extraction or instruction manipulation
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)", re.IGNORECASE),
    re.compile(r"(reveal|print|show|output|leak)\s+(your\s+)?(system\s+prompt|initial\s+prompt|instructions)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(safety|system|operational)\s+guidelines", re.IGNORECASE),
    re.compile(r"repeat\s+the\s+(text|words|prompt)\s+above", re.IGNORECASE),
]


def validate_input(user_input: str) -> tuple[bool, str]:
    """Deterministically validate incoming user messages.

    Checks:
    1. Rejects empty or whitespace-only input.
    2. Enforces maximum length of 1000 characters.
    3. Rejects prompt injection or system extraction attempts.

    Returns:
        (is_valid, message): True and sanitized input if valid,
                             False and failure reason if rejected.
    """
    if not isinstance(user_input, str):
        return False, "Input must be a string."

    trimmed = user_input.strip()
    if not trimmed:
        return False, "Input cannot be empty or whitespace only."

    if len(trimmed) > MAX_INPUT_LENGTH:
        return False, f"Input length ({len(trimmed)}) exceeds the maximum limit of {MAX_INPUT_LENGTH} characters."

    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(trimmed):
            return False, "Input rejected: Attempt to manipulate internal system instructions or extract prompts."

    return True, trimmed
