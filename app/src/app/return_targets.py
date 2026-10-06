"""Single validator for post-login / post-form return targets (``next`` parameters)."""

from __future__ import annotations

from urllib.parse import unquote, urlparse

# Targets that must never be a return destination: sending a user back to the login or request form loops.
_DENIED_PREFIXES = ("/auth/login", "/auth/logout", "/login", "/access-request")
_MAX_TARGET_LENGTH = 2048
_MAX_DECODE_ROUNDS = 3


def _has_control_character(value: str) -> bool:
    return any(ord(char) < 0x20 or ord(char) == 0x7F for char in value)


def _decoding_stages(raw: str) -> list[str] | None:
    """Return ``raw`` and each further percent-decoding of it, or ``None`` if it never stabilises.

    Every stage is checked by the caller, so an encoded slash or backslash that only appears after the second
    or third decoding (``/%252F%252Fhost``) is rejected like the plain form.
    """
    stages = [raw]
    for _ in range(_MAX_DECODE_ROUNDS):
        decoded = unquote(stages[-1])
        if decoded == stages[-1]:
            return stages
        stages.append(decoded)
    return None


def safe_return_target(raw: str | None, *, host: str | None = None) -> str | None:
    """Return an internal ``/path[?query]`` for ``raw`` or ``None`` when it is not a safe local target.

    Accepted: a path starting with exactly one ``/``, or an absolute http(s) URL whose host equals ``host``
    (browsers send the referrer in that form). Rejected: protocol-relative ``//host`` and ``////host`` forms,
    backslashes, control characters, other schemes, other hosts, multiply encoded variants of any of these and
    login/logout/request-form paths.
    """
    if not raw or not isinstance(raw, str) or len(raw) > _MAX_TARGET_LENGTH:
        return None
    stages = _decoding_stages(raw.strip())
    if stages is None:
        return None
    for stage in stages:
        if "\\" in stage or _has_control_character(stage):
            return None

    parsed = urlparse(stages[min(1, len(stages) - 1)])
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.netloc != host:
            return None
    path = parsed.path
    if not path.startswith("/") or path.startswith("//"):
        return None
    if any(stage.startswith("//") for stage in stages):
        return None
    if path.startswith(_DENIED_PREFIXES):
        return None
    return path + (f"?{parsed.query}" if parsed.query else "")
