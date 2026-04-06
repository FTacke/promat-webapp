from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


TARGET_CHANNELS = 1
TARGET_BITRATE = "160k"
TARGET_BITRATE_BPS = 160000
TARGET_BUF_SIZE = "320k"
LOUDNORM_FILTER = "loudnorm=I=-16:TP=-1.5:LRA=11"


def ensure_media_tools() -> None:
    missing = [tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required media tools: {joined}")


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        message = stderr or stdout or "unknown ffmpeg/ffprobe failure"
        raise RuntimeError(message) from exc


def ffprobe_json(path: Path) -> dict[str, object]:
    ensure_media_tools()
    result = _run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ]
    )
    return json.loads(result.stdout)


def probe_duration_seconds(path: Path) -> float:
    payload = ffprobe_json(path)
    format_payload = payload.get("format")
    if not isinstance(format_payload, dict):
        raise RuntimeError(f"ffprobe did not return format metadata for {path}")
    duration = format_payload.get("duration")
    if duration in (None, ""):
        raise RuntimeError(f"ffprobe did not return a duration for {path}")
    return float(duration)


def probe_audio_profile(path: Path) -> dict[str, object]:
    payload = ffprobe_json(path)
    streams = payload.get("streams")
    if not isinstance(streams, list):
        raise RuntimeError(f"ffprobe did not return stream metadata for {path}")
    audio_stream = next((stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "audio"), None)
    if not isinstance(audio_stream, dict):
        raise RuntimeError(f"No audio stream found in {path}")
    format_payload = payload.get("format")
    if not isinstance(format_payload, dict):
        format_payload = {}
    return {
        "codec_name": audio_stream.get("codec_name"),
        "channels": int(audio_stream.get("channels") or 0),
        "bit_rate": int(audio_stream.get("bit_rate") or format_payload.get("bit_rate") or 0),
        "format_name": format_payload.get("format_name"),
        "duration": float(format_payload.get("duration") or 0.0),
    }


def create_full_wordlist_mp3(source_wav: Path, target_mp3: Path) -> None:
    ensure_media_tools()
    target_mp3.parent.mkdir(parents=True, exist_ok=True)
    _run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source_wav),
            "-map",
            "a:0",
            "-vn",
            "-ac",
            str(TARGET_CHANNELS),
            "-c:a",
            "libmp3lame",
            "-b:a",
            TARGET_BITRATE,
            "-minrate",
            TARGET_BITRATE,
            "-maxrate",
            TARGET_BITRATE,
            "-bufsize",
            TARGET_BUF_SIZE,
            "-write_xing",
            "0",
            "-af",
            LOUDNORM_FILTER,
            str(target_mp3),
        ]
    )


def create_split_mp3(source_mp3: Path, target_mp3: Path, start_seconds: float, end_seconds: float) -> None:
    ensure_media_tools()
    if end_seconds <= start_seconds:
        raise ValueError(f"Invalid split boundaries for {target_mp3}: {start_seconds} >= {end_seconds}")
    target_mp3.parent.mkdir(parents=True, exist_ok=True)
    _run_command(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start_seconds:.4f}",
            "-to",
            f"{end_seconds:.4f}",
            "-i",
            str(source_mp3),
            "-map",
            "a:0",
            "-vn",
            "-ac",
            str(TARGET_CHANNELS),
            "-c:a",
            "libmp3lame",
            "-b:a",
            TARGET_BITRATE,
            "-minrate",
            TARGET_BITRATE,
            "-maxrate",
            TARGET_BITRATE,
            "-bufsize",
            TARGET_BUF_SIZE,
            "-write_xing",
            "0",
            str(target_mp3),
        ]
    )