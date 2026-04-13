"""Canonical research capability definitions and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Literal


RESEARCH_TASK_KEYS: tuple[str, ...] = ("wordlist", "text", "interview")
RESEARCH_PAGE_SLUGS: tuple[str, ...] = ("design", "speakers", "recordings", "comparison", "phenomena")
RESEARCH_DETAIL_ROUTE_KEYS: tuple[str, ...] = (
    "phenomena-preset-editor",
    "phenomena-set-editor",
    "player",
    "player-audio",
    "player-item-audio",
    "speaker-profile",
)
ACTIVE_RESEARCH_CORPORA: tuple[str, ...] = ("spanish", "french", "german", "english")
PLAYER_RENDER_MODES: tuple[str, ...] = ("sentence_list", "running_text")
PLAYER_VIEW_KEYS: tuple[str, ...] = ("list", "text")
COMPARISON_ALL_VIEW_KEY = "all"

TaskLabelVariant = Literal["short", "long", "material", "description"]
ResearchPageAccess = Literal["public", "protected"]
ResearchPageKind = Literal["reading", "workbench"]
ResearchPageSurfaceMode = Literal["content", "placeholder", "productive"]


@dataclass(frozen=True)
class ResearchTaskCapability:
    key: str
    long_label_de: str
    long_label_en: str
    short_label_de: str
    short_label_en: str
    material_label_de: str
    material_label_en: str
    description_de: str
    description_en: str
    visible_in_player: bool
    productive_in_player: bool
    supports_player_compare: bool
    supports_set_filtering: bool
    visible_in_comparison: bool
    visible_in_phenomena: bool
    supports_running_text: bool
    available_for_native_speakers: bool = True
    separate_flow: bool = False
    uses_catalog_display_label: bool = False

    def label(self, ui_lang: str, variant: TaskLabelVariant = "short") -> str:
        if variant == "long":
            return self.long_label_de if ui_lang == "de" else self.long_label_en
        if variant == "material":
            return self.material_label_de if ui_lang == "de" else self.material_label_en
        if variant == "description":
            return self.description_de if ui_lang == "de" else self.description_en
        return self.short_label_de if ui_lang == "de" else self.short_label_en

    def long_label(self, ui_lang: str) -> str:
        return self.label(ui_lang, "long")

    def short_label(self, ui_lang: str) -> str:
        return self.label(ui_lang, "short")

    def description(self, ui_lang: str) -> str:
        return self.label(ui_lang, "description")


@dataclass(frozen=True)
class ResearchPageCapability:
    slug: str
    label_key: str
    access: ResearchPageAccess
    page_kind: ResearchPageKind

    @property
    def requires_auth(self) -> bool:
        return self.access == "protected"


@dataclass(frozen=True)
class PlayerRenderCapability:
    default_render_mode: str | None
    allowed_render_modes: tuple[str, ...]
    supports_text_view: bool


RESEARCH_TASK_CAPABILITIES: tuple[ResearchTaskCapability, ...] = (
    ResearchTaskCapability(
        key="wordlist",
        long_label_de="Wortliste",
        long_label_en="Wordlist",
        short_label_de="Wortliste",
        short_label_en="Wordlist",
        material_label_de="Wortliste",
        material_label_en="Wordlist",
        description_de="Isolierte Aussprache über das Vorlesen einer Wortliste.",
        description_en="Pronunciation through reading a word list aloud.",
        visible_in_player=True,
        productive_in_player=True,
        supports_player_compare=True,
        supports_set_filtering=True,
        visible_in_comparison=True,
        visible_in_phenomena=True,
        supports_running_text=False,
        uses_catalog_display_label=True,
    ),
    ResearchTaskCapability(
        key="text",
        long_label_de="Text",
        long_label_en="Text",
        short_label_de="Text",
        short_label_en="Text",
        material_label_de="Satzliste",
        material_label_en="Sentence list",
        description_de="Zusammenhängende Aussprache über das Vorlesen eines Textes oder einer Satzliste.",
        description_en="Pronunciation through reading a text or sentence list aloud.",
        visible_in_player=True,
        productive_in_player=True,
        supports_player_compare=True,
        supports_set_filtering=True,
        visible_in_comparison=True,
        visible_in_phenomena=True,
        supports_running_text=True,
        uses_catalog_display_label=True,
    ),
    ResearchTaskCapability(
        key="interview",
        long_label_de="Interview zur Aussprache",
        long_label_en="Interview",
        short_label_de="Interview",
        short_label_en="Interview",
        material_label_de="Interview",
        material_label_en="Interview",
        description_de="Interview mit den Sprecher:innen zur Reflexion der Aussprache bzw. Aufzeichnung.",
        description_en="Semi-guided conversation with spontaneous pronunciation.",
        visible_in_player=True,
        productive_in_player=False,
        supports_player_compare=False,
        supports_set_filtering=False,
        visible_in_comparison=False,
        visible_in_phenomena=False,
        supports_running_text=False,
        available_for_native_speakers=False,
        separate_flow=True,
    ),
)

RESEARCH_PAGE_CAPABILITIES: tuple[ResearchPageCapability, ...] = (
    ResearchPageCapability(slug="design", label_key="research.design", access="public", page_kind="reading"),
    ResearchPageCapability(slug="speakers", label_key="research.speakers", access="protected", page_kind="workbench"),
    ResearchPageCapability(slug="recordings", label_key="research.recordings", access="protected", page_kind="workbench"),
    ResearchPageCapability(slug="comparison", label_key="research.comparison", access="protected", page_kind="workbench"),
    ResearchPageCapability(slug="phenomena", label_key="research.phenomena", access="protected", page_kind="workbench"),
)

RESEARCH_TASK_CAPABILITY_MAP = {capability.key: capability for capability in RESEARCH_TASK_CAPABILITIES}
RESEARCH_PAGE_CAPABILITY_MAP = {capability.slug: capability for capability in RESEARCH_PAGE_CAPABILITIES}

DEFAULT_RESEARCH_PAGE_SURFACE_MODES: dict[str, ResearchPageSurfaceMode] = {
    "design": "content",
    "speakers": "placeholder",
    "recordings": "placeholder",
    "comparison": "placeholder",
    "phenomena": "placeholder",
}

CORPUS_RESEARCH_PAGE_SURFACE_OVERRIDES: dict[str, dict[str, ResearchPageSurfaceMode]] = {
    "spanish": {
        "speakers": "productive",
        "recordings": "productive",
        "comparison": "productive",
        "phenomena": "productive",
    }
}


def _render_mode_to_view(render_mode: str) -> str:
    if render_mode == "running_text":
        return "text"
    return "list"


def _render_mode_from_view(view_key: str | None) -> str:
    if view_key == "text":
        return "running_text"
    return "sentence_list"


def iter_research_task_capabilities() -> Iterable[ResearchTaskCapability]:
    return RESEARCH_TASK_CAPABILITIES


def get_research_task_capability(task_key: str) -> ResearchTaskCapability | None:
    return RESEARCH_TASK_CAPABILITY_MAP.get((task_key or "").strip())


def iter_research_page_capabilities() -> Iterable[ResearchPageCapability]:
    return RESEARCH_PAGE_CAPABILITIES


def get_research_page_capability(page_slug: str) -> ResearchPageCapability | None:
    return RESEARCH_PAGE_CAPABILITY_MAP.get((page_slug or "").strip())


def get_research_page_order() -> tuple[tuple[str, str], ...]:
    return tuple((capability.slug, capability.label_key) for capability in RESEARCH_PAGE_CAPABILITIES)


def get_research_page_surface_mode(language_slug: str, page_slug: str) -> ResearchPageSurfaceMode | None:
    capability = get_research_page_capability(page_slug)
    if capability is None:
        return None
    normalized_language = (language_slug or "").strip().lower()
    override = CORPUS_RESEARCH_PAGE_SURFACE_OVERRIDES.get(normalized_language, {}).get(capability.slug)
    if override is not None:
        return override
    return DEFAULT_RESEARCH_PAGE_SURFACE_MODES[capability.slug]


def is_public_research_page(page_slug: str) -> bool:
    capability = get_research_page_capability(page_slug)
    return capability is not None and capability.access == "public"


def requires_research_auth(*, page_slug: str | None = None, detail_route: str | None = None) -> bool:
    normalized_page_slug = (page_slug or "").strip()
    normalized_detail_route = (detail_route or "").strip()
    if normalized_page_slug and normalized_detail_route:
        raise ValueError("Specify either page_slug or detail_route for research capability checks, not both")
    if normalized_page_slug:
        capability = get_research_page_capability(normalized_page_slug)
        if capability is None:
            raise ValueError(f"Unsupported research page '{normalized_page_slug}'")
        return capability.requires_auth
    if normalized_detail_route:
        if normalized_detail_route not in RESEARCH_DETAIL_ROUTE_KEYS:
            raise ValueError(f"Unsupported research detail route '{normalized_detail_route}'")
        return True
    raise ValueError("Research capability checks require a page_slug or detail_route")


def player_visible_task_keys() -> tuple[str, ...]:
    return tuple(capability.key for capability in RESEARCH_TASK_CAPABILITIES if capability.visible_in_player)


def player_productive_task_keys() -> tuple[str, ...]:
    return tuple(capability.key for capability in RESEARCH_TASK_CAPABILITIES if capability.productive_in_player)


def player_compare_task_keys() -> tuple[str, ...]:
    return tuple(capability.key for capability in RESEARCH_TASK_CAPABILITIES if capability.supports_player_compare)


def set_filter_task_keys() -> tuple[str, ...]:
    return tuple(capability.key for capability in RESEARCH_TASK_CAPABILITIES if capability.supports_set_filtering)


def phenomena_task_keys() -> tuple[str, ...]:
    return tuple(capability.key for capability in RESEARCH_TASK_CAPABILITIES if capability.visible_in_phenomena)


def comparison_view_task_keys(*, include_all: bool = True) -> tuple[str, ...]:
    task_keys = tuple(capability.key for capability in RESEARCH_TASK_CAPABILITIES if capability.visible_in_comparison)
    if include_all:
        return (COMPARISON_ALL_VIEW_KEY,) + task_keys
    return task_keys


def comparison_default_view_task() -> str:
    comparison_tasks = comparison_view_task_keys(include_all=False)
    if not comparison_tasks:
        raise RuntimeError("At least one comparison-capable research task is required")
    return comparison_tasks[0]


def is_task_available_for_speaker_type(task_key: str, speaker_type: str) -> bool:
    capability = get_research_task_capability(task_key)
    if capability is None:
        return False
    if speaker_type == "native_speaker" and not capability.available_for_native_speakers:
        return False
    return True


def available_task_keys_for_session(documented_task_types: Iterable[str], speaker_type: str) -> tuple[str, ...]:
    documented = {task_key for task_key in documented_task_types if get_research_task_capability(task_key) is not None}
    return tuple(
        capability.key
        for capability in RESEARCH_TASK_CAPABILITIES
        if capability.key in documented and is_task_available_for_speaker_type(capability.key, speaker_type)
    )


def task_supports_set_filtering(task_key: str) -> bool:
    capability = get_research_task_capability(task_key)
    return capability is not None and capability.supports_set_filtering


def task_supports_player_compare(task_key: str) -> bool:
    capability = get_research_task_capability(task_key)
    return capability is not None and capability.supports_player_compare


def get_research_task_label(task_key: str, ui_lang: str, *, variant: TaskLabelVariant = "short", language_slug: str | None = None) -> str:
    capability = get_research_task_capability(task_key)
    if capability is None:
        return task_key
    if variant == "material" and ui_lang == "de" and language_slug and capability.uses_catalog_display_label:
        try:
            from .research_presets import ResearchConfigError, load_task_catalogs

            catalog = load_task_catalogs(language_slug).get(task_key)
        except ResearchConfigError:
            catalog = None
        if catalog is not None and catalog.display_label:
            return catalog.display_label
    return capability.label(ui_lang, variant)


@lru_cache(maxsize=128)
def resolve_player_render_capability(
    task_key: str,
    *,
    source_allowed_views: tuple[str, ...] | None,
    source_default_view: str | None,
    compare_selected: bool,
    is_set_excerpt: bool,
) -> PlayerRenderCapability:
    capability = get_research_task_capability(task_key)
    if capability is None or not capability.productive_in_player or not capability.supports_running_text:
        return PlayerRenderCapability(default_render_mode=None, allowed_render_modes=(), supports_text_view=False)

    normalized_allowed_views = tuple(view_key for view_key in (source_allowed_views or ("list",)) if view_key in PLAYER_VIEW_KEYS) or ("list",)
    supports_text_view = not is_set_excerpt and not compare_selected and "text" in normalized_allowed_views
    if not supports_text_view:
        return PlayerRenderCapability(
            default_render_mode="sentence_list",
            allowed_render_modes=("sentence_list",),
            supports_text_view=False,
        )

    allowed_render_modes = tuple(
        render_mode for render_mode in PLAYER_RENDER_MODES if _render_mode_to_view(render_mode) in normalized_allowed_views
    ) or ("sentence_list",)
    default_render_mode = _render_mode_from_view(source_default_view)
    if default_render_mode not in allowed_render_modes:
        default_render_mode = allowed_render_modes[0]
    return PlayerRenderCapability(
        default_render_mode=default_render_mode,
        allowed_render_modes=allowed_render_modes,
        supports_text_view=True,
    )