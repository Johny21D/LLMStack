"""Utilities for redacting secrets from text before it is logged.

LLMStack routes user prompts, tool output, and provider responses through
its logs. Those strings occasionally contain API keys or access tokens.
This module masks common secret formats so raw credentials never land in
plaintext logs.

The module intentionally has no Django or third-party dependencies so it
can be imported and unit-tested in isolation.
"""

import re

_MASK = "[REDACTED]"

# (label, compiled pattern). More specific patterns are listed first so a
# narrowly-formatted secret (e.g. an Anthropic key) is masked before a more
# general pattern can match part of it.
_SECRET_PATTERNS = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
]


def redact_secrets(text):
    """Return *text* with recognized secret tokens replaced by a mask.

    Args:
        text: The string to scan. Non-string inputs are returned unchanged
            so this is safe to call defensively on arbitrary log payloads.

    Returns:
        A copy of the string with any matched secrets replaced by
        ``[REDACTED]``. If no secrets are found, the original string is
        returned unchanged.
    """
    if not isinstance(text, str):
        return text

    redacted = text
    for _label, pattern in _SECRET_PATTERNS:
        redacted = pattern.sub(_MASK, redacted)
    return redacted


def contains_secret(text):
    """Return True if *text* appears to contain a recognized secret token."""
    if not isinstance(text, str):
        return False
    return any(pattern.search(text) for _label, pattern in _SECRET_PATTERNS)
