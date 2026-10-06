"""Read and strip container tags (ID3v2, ID3v1, APEv2) of web MP3 files without extra dependencies.

Why this exists: ffmpeg copies the tags of its source recording into every derived MP3 unless it is told not to,
so runtime audio once shipped source titles such as ``<Name>_Liste_ENG`` (audit finding DATA-01). The released
web MP3s of the research corpus are policy-bound to carry **no descriptive tags**:

* ID3v2 frames: none, except encoder bookkeeping frames (``TSSE``, ``TENC``) whose text is a software name
  and version; they contain no recording or person information. ``PRIV`` / ``COMM`` / ``TIT2`` / ``TPE1`` /
  ``TALB`` and everything else are rejected.
* ID3v1 (trailing 128 bytes) and APEv2 footers: none.

``strip_tags`` removes the tag bytes and leaves every MPEG audio frame byte-for-byte unchanged (no re-encoding).
Values are never printed by the tools that use this module, only frame ids and counts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

ALLOWED_ID3V2_FRAMES = frozenset({"TSSE", "TENC"})
_ID3V1_SIZE = 128
_APE_FOOTER = b"APETAGEX"


@dataclass
class TagReport:
    path: Path
    id3v2_frames: dict[str, list[str]] = field(default_factory=dict)
    id3v2_size: int = 0
    id3v1: bool = False
    apev2: bool = False
    error: str | None = None

    @property
    def disallowed(self) -> list[str]:
        """Names of the tag parts that violate the web-audio policy (frame ids only, no values)."""
        problems = [f"id3v2:{frame}" for frame in sorted(self.id3v2_frames) if frame not in ALLOWED_ID3V2_FRAMES]
        if self.id3v1:
            problems.append("id3v1")
        if self.apev2:
            problems.append("apev2")
        if self.error:
            problems.append(f"unreadable:{self.error}")
        return problems


def _syncsafe(raw: bytes) -> int:
    return (raw[0] << 21) | (raw[1] << 14) | (raw[2] << 7) | raw[3]


def _decode_text(payload: bytes) -> str:
    if not payload:
        return ""
    encoding = {0: "latin-1", 1: "utf-16", 2: "utf-16-be", 3: "utf-8"}.get(payload[0], "latin-1")
    try:
        return payload[1:].decode(encoding, errors="replace").strip("\x00 ")
    except LookupError:  # pragma: no cover - defensive
        return ""


def _parse_id3v2(header: bytes, body: bytes) -> dict[str, list[str]]:
    version = header[3]
    frames: dict[str, list[str]] = {}
    position = 0
    # Unsynchronisation / extended header are not expected in files written by ffmpeg; parse what is plain.
    if header[5] & 0x40 and len(body) >= 4:
        ext_size = _syncsafe(body[:4]) if version == 4 else int.from_bytes(body[:4], "big") + 4
        position = ext_size
    while position + 10 <= len(body):
        frame_id = body[position : position + 4]
        if frame_id[0] == 0 or not all(65 <= byte <= 90 or 48 <= byte <= 57 for byte in frame_id):
            break  # padding or garbage
        size = _syncsafe(body[position + 4 : position + 8]) if version == 4 else int.from_bytes(body[position + 4 : position + 8], "big")
        payload = body[position + 10 : position + 10 + size]
        name = frame_id.decode("ascii")
        text = _decode_text(payload) if name.startswith("T") and name != "TXXX" else ""
        frames.setdefault(name, []).append(text)
        position += 10 + size
    return frames


def read_tags(path: Path) -> TagReport:
    report = TagReport(path=path)
    try:
        with open(path, "rb") as handle:
            header = handle.read(10)
            if len(header) == 10 and header[:3] == b"ID3":
                report.id3v2_size = 10 + _syncsafe(header[6:10]) + (10 if header[5] & 0x10 else 0)
                report.id3v2_frames = _parse_id3v2(header, handle.read(report.id3v2_size - 10))
            handle.seek(0, 2)
            length = handle.tell()
            if length >= _ID3V1_SIZE:
                handle.seek(length - _ID3V1_SIZE)
                report.id3v1 = handle.read(3) == b"TAG"
            if length >= 32:
                handle.seek(length - 32)
                report.apev2 = handle.read(8) == _APE_FOOTER
                if not report.apev2 and length >= _ID3V1_SIZE + 32:
                    handle.seek(length - _ID3V1_SIZE - 32)
                    report.apev2 = handle.read(8) == _APE_FOOTER
    except OSError as exc:
        report.error = type(exc).__name__
    return report


def strip_tags(source: Path, target: Path) -> TagReport:
    """Write ``source`` without ID3v2 / ID3v1 / APEv2 tags to ``target``; the MPEG frames are copied unchanged.

    Returns the report of the *source*. Refuses an APEv2 tag (not produced by our pipeline) instead of guessing.
    """
    report = read_tags(source)
    if report.error:
        raise OSError(f"cannot read {source.name}: {report.error}")
    if report.apev2:
        raise ValueError(f"{source.name}: APEv2 tag found; strip it with a tool that understands it")
    data = source.read_bytes()
    start = report.id3v2_size
    end = len(data) - _ID3V1_SIZE if report.id3v1 else len(data)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data[start:end])
    return report
