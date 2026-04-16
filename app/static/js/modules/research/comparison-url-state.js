function resolveBaseOrigin(baseOrigin = null) {
  if (baseOrigin) {
    return baseOrigin;
  }
  if (typeof window !== "undefined" && window.location && window.location.origin) {
    return window.location.origin;
  }
  return "http://localhost";
}

function normalizeLevels(levels) {
  const rawValues = Array.isArray(levels)
    ? levels
    : typeof levels === "string"
      ? levels.split(",")
      : [];
  return Array.from(new Set(rawValues
    .map((value) => String(value || "").trim().toUpperCase())
    .filter(Boolean)));
}

export function parseComparisonUrlState(urlLike, baseOrigin = null) {
  const origin = resolveBaseOrigin(baseOrigin);
  const parsed = new URL(urlLike || origin, origin);
  return {
    setId: parsed.searchParams.get("set_id") || null,
    task: parsed.searchParams.get("task") || null,
    filters: {
      search: parsed.searchParams.get("search") || "",
      levels: normalizeLevels(parsed.searchParams.get("levels") || ""),
      l1: parsed.searchParams.get("l1") || "",
      gender: parsed.searchParams.get("gender") || "",
      exposure: parsed.searchParams.get("exposure") || "",
    },
  };
}

export function shouldExposeComparisonSetId({
  activeSetId = null,
  requestedSetId = null,
  isImplicitDraft = false,
  isDefaultCompleteSet = false,
  selectedSessionIds = [],
} = {}) {
  if (!activeSetId) {
    return false;
  }
  if (requestedSetId) {
    return true;
  }
  if (!isImplicitDraft) {
    return true;
  }
  return Boolean((selectedSessionIds || []).length || !isDefaultCompleteSet);
}

export function buildComparisonStateUrl(baseHref, { setId = null, task = null, filters = {} } = {}, baseOrigin = null) {
  const origin = resolveBaseOrigin(baseOrigin);
  const url = new URL(baseHref || origin, origin);
  const normalizedLevels = normalizeLevels(filters.levels || []);
  const nextFilters = {
    search: String(filters.search || "").trim(),
    l1: String(filters.l1 || "").trim(),
    gender: String(filters.gender || "").trim(),
    exposure: String(filters.exposure || "").trim(),
  };

  if (setId) {
    url.searchParams.set("set_id", setId);
  } else {
    url.searchParams.delete("set_id");
  }

  if (task) {
    url.searchParams.set("task", task);
  } else {
    url.searchParams.delete("task");
  }

  if (nextFilters.search) {
    url.searchParams.set("search", nextFilters.search);
  } else {
    url.searchParams.delete("search");
  }

  if (normalizedLevels.length) {
    url.searchParams.set("levels", normalizedLevels.join(","));
  } else {
    url.searchParams.delete("levels");
  }

  if (nextFilters.l1) {
    url.searchParams.set("l1", nextFilters.l1);
  } else {
    url.searchParams.delete("l1");
  }

  if (nextFilters.gender) {
    url.searchParams.set("gender", nextFilters.gender);
  } else {
    url.searchParams.delete("gender");
  }

  if (nextFilters.exposure) {
    url.searchParams.set("exposure", nextFilters.exposure);
  } else {
    url.searchParams.delete("exposure");
  }

  return `${url.pathname}${url.search}`;
}