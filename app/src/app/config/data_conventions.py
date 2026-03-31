"""Canonical technical vocabularies for PROMAT data and session metadata."""

from __future__ import annotations


SPEAKER_TYPES: tuple[str, ...] = (
    "learner",
    "native_speaker",
    "heritage_speaker",
)

TARGET_LANGUAGES: tuple[str, ...] = ("es", "fr", "en", "de")

TASK_TYPES: tuple[str, ...] = (
    "isolated_speech",
    "connected_speech",
    "interview",
)

CONTEXT_VALUES: tuple[str, ...] = ("baseline", "follow_up")

FILE_ROLES: tuple[str, ...] = (
    "audio_raw",
    "audio_source",
    "audio_mp3",
    "textgrid",
    "items_audio",
    "items_json",
    "metadata",
)

STANDARD_VARIETIES: dict[str, tuple[str, ...]] = {
    "es": ("es_std", "mx_std", "ar_std", "co_std", "cl_std"),
    "en": ("gb_std", "us_std", "au_std", "nz_std"),
    "fr": ("fr_std", "ca_std", "ch_std", "be_std"),
    "de": ("de_std", "at_std", "ch_std", "de_south_std"),
}
