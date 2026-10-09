// Carries the comparison workspace that lives only in page memory (selected speakers and a built-in material preset)
// across a UI-language switch. The switch is a full page load, so the page hands the state over through sessionStorage:
// written only when a language-switch link is activated, read once by the next comparison page, then removed.
// Only stable ids are stored (never labels); the reader validates them against the corpus catalog it just received.

export const COMPARISON_LANG_HANDOFF_KEY = "pm.comparison.langSwitch";
export const COMPARISON_LANG_HANDOFF_MAX_AGE_MS = 2 * 60 * 1000;

function uniqueStrings(values) {
  return Array.from(new Set((Array.isArray(values) ? values : []).filter((value) => typeof value === "string" && value)));
}

export function saveComparisonLangHandoff(storage, { corpus, sessionIds, presetId = null, now = Date.now() }) {
  if (!storage || !corpus) {
    return false;
  }
  const ids = uniqueStrings(sessionIds);
  try {
    if (!ids.length && !presetId) {
      storage.removeItem(COMPARISON_LANG_HANDOFF_KEY);
      return false;
    }
    storage.setItem(
      COMPARISON_LANG_HANDOFF_KEY,
      JSON.stringify({ corpus, sessionIds: ids, presetId: presetId || null, at: now }),
    );
    return true;
  } catch {
    return false;
  }
}

// Returns { sessionIds, presetId } and always clears the entry. Anything stale, from another corpus, or not valid in the
// current catalog is dropped.
export function takeComparisonLangHandoff(storage, { corpus, validSessionIds, now = Date.now() }) {
  const empty = { sessionIds: [], presetId: null };
  if (!storage) {
    return empty;
  }
  let raw = null;
  try {
    raw = storage.getItem(COMPARISON_LANG_HANDOFF_KEY);
    storage.removeItem(COMPARISON_LANG_HANDOFF_KEY);
  } catch {
    return empty;
  }
  if (!raw) {
    return empty;
  }
  let parsed = null;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return empty;
  }
  if (!parsed || parsed.corpus !== corpus || !(now - Number(parsed.at) >= 0) || now - Number(parsed.at) > COMPARISON_LANG_HANDOFF_MAX_AGE_MS) {
    return empty;
  }
  const valid = validSessionIds instanceof Set ? validSessionIds : new Set(validSessionIds || []);
  return {
    sessionIds: uniqueStrings(parsed.sessionIds).filter((id) => valid.has(id)),
    presetId: typeof parsed.presetId === "string" && parsed.presetId ? parsed.presetId : null,
  };
}

export function safeSessionStorage() {
  try {
    return typeof window !== "undefined" ? window.sessionStorage : null;
  } catch {
    return null;
  }
}
