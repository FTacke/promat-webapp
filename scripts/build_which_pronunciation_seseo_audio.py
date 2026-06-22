from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from research_data_intake.audio_conversion.ffmpeg_audio import ensure_media_tools, ffprobe_json


REPO_ROOT = Path(__file__).resolve().parents[1]
SESSION_ID = "ES-N-0004-2026-S01"
SESSION_ROOT = REPO_ROOT / "data" / "sessions" / "spanish" / SESSION_ID
ALIGNMENT_PATH = SESSION_ROOT / "alignment" / "wordlist.json"
OUTPUT_ROOT = (
    REPO_ROOT
    / "content"
    / "teaching"
    / "spanish"
    / "which-pronunciation"
    / "media"
    / "audio"
    / "variation"
)
OUTPUT_SAMPLE_RATE = 44_100
OUTPUT_BITRATE = "96k"
SILENCE_SECONDS = 0.2
SILENCE_SAMPLES = int(OUTPUT_SAMPLE_RATE * SILENCE_SECONDS)


@dataclass(frozen=True)
class Recipe:
    filename: str
    items: tuple[tuple[str, str], ...]


RECIPES = (
    Recipe(
        filename="seseo-casa-caza-es-n-0004-2026-s01.mp3",
        items=(("wl_065", "casa"), ("wl_034", "caza")),
    ),
    Recipe(
        filename="seseo-word-series-es-n-0004-2026-s01.mp3",
        items=(
            ("wl_063", "gracias"),
            ("wl_008", "ciudad"),
            ("wl_071", "paz"),
            ("wl_066", "ración"),
        ),
    ),
)


def _run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "unknown ffmpeg failure").strip()
        raise RuntimeError(message) from exc


def _load_items() -> dict[str, dict[str, object]]:
    payload = json.loads(ALIGNMENT_PATH.read_text(encoding="utf-8"))
    if payload.get("session_id") != SESSION_ID or payload.get("task") != "wordlist":
        raise RuntimeError(f"Unexpected alignment source: {ALIGNMENT_PATH}")
    return {str(item["item_id"]): item for item in payload["items"]}


def _source_paths(recipe: Recipe, items: dict[str, dict[str, object]]) -> list[Path]:
    paths: list[Path] = []
    for item_id, expected_text in recipe.items:
        item = items.get(item_id)
        if not item or item.get("text") != expected_text:
            actual = None if item is None else item.get("text")
            raise RuntimeError(f"Expected {item_id}={expected_text!r}, found {actual!r}")
        source = SESSION_ROOT / str(item["split_mp3"])
        if not source.is_file():
            raise FileNotFoundError(source)
        paths.append(source)
    return paths


def _filter_graph(source_count: int) -> str:
    filters: list[str] = []
    concat_inputs: list[str] = []
    for index in range(source_count):
        filters.append(
            f"[{index}:a]aresample={OUTPUT_SAMPLE_RATE},"
            f"aformat=sample_fmts=fltp:channel_layouts=mono[a{index}]"
        )
        concat_inputs.append(f"[a{index}]")
        if index < source_count - 1:
            filters.append(
                f"anullsrc=r={OUTPUT_SAMPLE_RATE}:cl=mono,"
                f"atrim=end_sample={SILENCE_SAMPLES}[s{index}]"
            )
            concat_inputs.append(f"[s{index}]")
    concat = "".join(concat_inputs)
    filters.append(f"{concat}concat=n={len(concat_inputs)}:v=0:a=1[out]")
    return ";".join(filters)


def _build(recipe: Recipe, sources: list[Path]) -> Path:
    output = OUTPUT_ROOT / recipe.filename
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-y"]
    for source in sources:
        command.extend(("-i", str(source)))
    command.extend(
        (
            "-filter_complex",
            _filter_graph(len(sources)),
            "-map",
            "[out]",
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(OUTPUT_SAMPLE_RATE),
            "-c:a",
            "libmp3lame",
            "-b:a",
            OUTPUT_BITRATE,
            "-map_metadata",
            "-1",
            str(output),
        )
    )
    _run(command)
    return output


def _validate_output(output: Path) -> float:
    payload = ffprobe_json(output)
    audio_streams = [stream for stream in payload["streams"] if stream.get("codec_type") == "audio"]
    if len(audio_streams) != 1:
        raise RuntimeError(f"Expected one audio stream in {output}")
    stream = audio_streams[0]
    duration = float(payload["format"]["duration"])
    if (
        stream.get("codec_name") != "mp3"
        or int(stream.get("sample_rate", 0)) != OUTPUT_SAMPLE_RATE
        or int(stream.get("channels", 0)) != 1
        or duration <= 0
    ):
        raise RuntimeError(f"Unexpected output profile for {output}: {stream}")
    return duration


def main() -> None:
    ensure_media_tools()
    items = _load_items()
    for recipe in RECIPES:
        sources = _source_paths(recipe, items)
        output = _build(recipe, sources)
        duration = _validate_output(output)
        source_labels = ", ".join(f"{item_id}={text}" for item_id, text in recipe.items)
        print(f"{output.relative_to(REPO_ROOT)} ({duration:.3f}s) <- {source_labels}")


if __name__ == "__main__":
    main()
