from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntakeLanguageConfig:
    code: str
    corpus_slug: str
    display_name: str
    mfa_acoustic_model: str
    mfa_dictionary_model: str
    tokenization_profile: str
    normalization_profile: str


LANGUAGE_CONFIGS: dict[str, IntakeLanguageConfig] = {
    "es": IntakeLanguageConfig(
        code="es",
        corpus_slug="spanish",
        display_name="Spanish",
        mfa_acoustic_model="spanish_mfa",
        mfa_dictionary_model="spanish_mfa",
        tokenization_profile="canonical_target_words",
        normalization_profile="no_silent_normalization",
    ),
    "de": IntakeLanguageConfig(
        code="de",
        corpus_slug="german",
        display_name="German",
        mfa_acoustic_model="german_mfa",
        mfa_dictionary_model="german_mfa",
        tokenization_profile="canonical_target_words",
        normalization_profile="no_silent_normalization",
    ),
    "fr": IntakeLanguageConfig(
        code="fr",
        corpus_slug="french",
        display_name="French",
        mfa_acoustic_model="french_mfa",
        mfa_dictionary_model="french_mfa",
        tokenization_profile="canonical_target_words",
        normalization_profile="no_silent_normalization",
    ),
    "en": IntakeLanguageConfig(
        code="en",
        corpus_slug="english",
        display_name="English",
        mfa_acoustic_model="english_mfa",
        mfa_dictionary_model="english_mfa",
        tokenization_profile="canonical_target_words",
        normalization_profile="no_silent_normalization",
    ),
}

_LANGUAGE_ALIASES: dict[str, str] = {}
for config in LANGUAGE_CONFIGS.values():
    _LANGUAGE_ALIASES[config.code] = config.code
    _LANGUAGE_ALIASES[config.corpus_slug] = config.code
    _LANGUAGE_ALIASES[config.display_name.lower()] = config.code


def supported_language_codes() -> tuple[str, ...]:
    return tuple(LANGUAGE_CONFIGS)


def iter_language_configs(codes: list[str] | None = None) -> list[IntakeLanguageConfig]:
    if codes is None:
        return [LANGUAGE_CONFIGS[code] for code in supported_language_codes()]
    return [resolve_language_config(code) for code in codes]


def resolve_language_config(value: str) -> IntakeLanguageConfig:
    normalized = value.strip().lower()
    language_code = _LANGUAGE_ALIASES.get(normalized)
    if language_code is None:
        supported = ", ".join(supported_language_codes())
        raise ValueError(f"Unsupported intake language {value!r}; expected one of: {supported}")
    return LANGUAGE_CONFIGS[language_code]


def maybe_resolve_language_config(value: str | None) -> IntakeLanguageConfig | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return resolve_language_config(stripped)


def describe_language_config(config: IntakeLanguageConfig) -> str:
    return (
        f"{config.code} ({config.corpus_slug}) acoustic={config.mfa_acoustic_model} "
        f"dictionary={config.mfa_dictionary_model}"
    )