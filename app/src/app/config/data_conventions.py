"""Canonical technical vocabularies for PROMAT data and session metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass


SPEAKER_TYPES: tuple[str, ...] = (
    "learner",
    "native_speaker",
)

TARGET_LANGUAGES: tuple[str, ...] = ("es", "fr", "en", "de")

TASK_TYPES: tuple[str, ...] = (
    "wordlist",
    "text",
    "interview",
)

CONTEXT_VALUES: tuple[str, ...] = ("baseline", "follow_up")

FILE_ROLES: tuple[str, ...] = (
    "audio_raw",
    "audio_source",
    "audio_mp3",
    "textgrid",
    "alignment_json",
    "items_audio",
    "metadata",
)

STANDARD_VARIETIES: dict[str, tuple[str, ...]] = {
    "es": ("es_std", "mx_std", "ar_std", "co_std", "cl_std"),
    "en": ("gb_std", "us_std", "au_std", "nz_std"),
    "fr": ("fr_std", "ca_std", "fr_ch_std", "be_std"),
    "de": ("de_std", "at_std", "de_ch_std", "de_south_std"),
}

LANGUAGE_SLUG_TO_TARGET_LANGUAGE: dict[str, str] = {
    "spanish": "es",
    "english": "en",
    "french": "fr",
    "german": "de",
}

TARGET_LANGUAGE_TO_CORPUS_CODE: dict[str, str] = {
    "es": "ES",
    "en": "EN",
    "fr": "FR",
    "de": "DE",
}

SPEAKER_TYPE_TO_ID_MARKER: dict[str, str] = {
    "learner": "L",
    "native_speaker": "N",
}

ID_MARKER_TO_SPEAKER_TYPE: dict[str, str] = {
    marker: speaker_type for speaker_type, marker in SPEAKER_TYPE_TO_ID_MARKER.items()
}

PERSON_ID_PATTERN = re.compile(r"^(?P<corpus_code>[A-Z]{2})-(?P<speaker_marker>[LN])-(?P<sequence>\d{4})$")
SESSION_ID_PATTERN = re.compile(
    r"^(?P<person_id>[A-Z]{2}-[LN]-\d{4})-(?P<recording_year>\d{4})-S(?P<session_number>\d{2})$"
)


@dataclass(frozen=True)
class PersonIdParts:
    corpus_code: str
    speaker_marker: str
    sequence: int

    @property
    def speaker_type(self) -> str | None:
        return ID_MARKER_TO_SPEAKER_TYPE.get(self.speaker_marker)

    @property
    def person_id(self) -> str:
        return f"{self.corpus_code}-{self.speaker_marker}-{self.sequence:04d}"


@dataclass(frozen=True)
class SessionIdParts:
    person_id: str
    recording_year: int
    session_number: int

    @property
    def session_id(self) -> str:
        return f"{self.person_id}-{self.recording_year:04d}-S{self.session_number:02d}"


def get_target_language_for_language_slug(language_slug: str) -> str | None:
    return LANGUAGE_SLUG_TO_TARGET_LANGUAGE.get(language_slug)


def get_corpus_code_for_target_language(target_language: str) -> str | None:
    return TARGET_LANGUAGE_TO_CORPUS_CODE.get((target_language or "").strip().lower())


def get_corpus_code_for_language_slug(language_slug: str) -> str | None:
    target_language = get_target_language_for_language_slug(language_slug)
    if target_language is None:
        return None
    return get_corpus_code_for_target_language(target_language)


def parse_person_id(person_id: str) -> PersonIdParts | None:
    match = PERSON_ID_PATTERN.fullmatch((person_id or "").strip())
    if match is None:
        return None
    return PersonIdParts(
        corpus_code=match.group("corpus_code"),
        speaker_marker=match.group("speaker_marker"),
        sequence=int(match.group("sequence")),
    )


def build_person_id(target_language: str, speaker_type: str, sequence: int) -> str:
    corpus_code = get_corpus_code_for_target_language(target_language)
    speaker_marker = SPEAKER_TYPE_TO_ID_MARKER.get(speaker_type)
    if corpus_code is None:
        raise ValueError(f"Unsupported target_language for person_id: {target_language}")
    if speaker_marker is None:
        raise ValueError(f"Unsupported speaker_type for person_id: {speaker_type}")
    if sequence <= 0:
        raise ValueError("sequence must be greater than 0")
    return f"{corpus_code}-{speaker_marker}-{sequence:04d}"


def parse_session_id(session_id: str) -> SessionIdParts | None:
    match = SESSION_ID_PATTERN.fullmatch((session_id or "").strip())
    if match is None:
        return None
    return SessionIdParts(
        person_id=match.group("person_id"),
        recording_year=int(match.group("recording_year")),
        session_number=int(match.group("session_number")),
    )


def build_session_id(person_id: str, recording_year: int, session_number: int) -> str:
    if parse_person_id(person_id) is None:
        raise ValueError(f"Unsupported person_id for session_id: {person_id}")
    if recording_year < 1000 or recording_year > 9999:
        raise ValueError("recording_year must be a four-digit year")
    if session_number <= 0 or session_number > 99:
        raise ValueError("session_number must be between 1 and 99")
    return f"{person_id}-{recording_year:04d}-S{session_number:02d}"
