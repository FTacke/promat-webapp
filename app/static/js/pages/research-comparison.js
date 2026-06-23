import { getCsrfToken } from "../api.js";
import { fetchWithAuth } from "../modules/auth/fetch.js";
import {
  buildComparisonStateUrl,
  parseComparisonUrlState,
  shouldExposeComparisonSetId,
} from "../modules/research/comparison-url-state.js";

let requestFailedLabel = "";

function parseState() {
  const element = document.getElementById("pm-comparison-state");
  if (!element) {
    return null;
  }

  try {
    const parsed = JSON.parse(element.textContent || "{}");
    return parsed && Array.isArray(parsed.sessionCatalog) ? parsed : null;
  } catch {
    return null;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function buildQueryUrl(baseHref, query) {
  const url = new URL(baseHref, window.location.origin);
  Object.entries(query).forEach(([key, value]) => {
    if (value === null || value === undefined || value === "") {
      url.searchParams.delete(key);
      return;
    }
    url.searchParams.set(key, value);
  });
  return `${url.pathname}${url.search}`;
}

function iconSvg(kind) {
  if (kind === "save") {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 4h10l4 4v12H6z" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"></path><path d="M9 4v6h6V4" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"></path><path d="M9 17h6" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.8"></path></svg>';
  }
  if (kind === "check") {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6.5 12.5l3.5 3.5 7.5-8" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>';
  }
  if (kind === "play") {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8 6l10 6-10 6z" fill="currentColor"></path></svg>';
  }
  if (kind === "stop") {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 7h10v10H7z" fill="currentColor"></path></svg>';
  }
  if (kind === "download") {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 5v9" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.8"></path><path d="M8.5 11.5L12 15l3.5-3.5" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"></path><path d="M6 18h12" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.8"></path></svg>';
  }
  if (kind === "add") {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 6v12" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.8"></path><path d="M6 12h12" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.8"></path></svg>';
  }
  if (kind === "remove") {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 12h12" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.8"></path></svg>';
  }
  if (kind === "close") {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8 8l8 8" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.9"></path><path d="M16 8l-8 8" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.9"></path></svg>';
  }
  return "";
}

async function requestJson(url, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
  };

  let body = options.body;
  if (body && typeof body === "object" && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
    body = JSON.stringify(body);
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }

  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers["X-CSRF-TOKEN"] = csrfToken;
    }
  }

  const response = await fetchWithAuth(url, {
    ...options,
    method,
    headers,
    body,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json().catch(() => null) : null;

  if (!response.ok) {
    const error = new Error((payload && payload.error) || response.statusText || requestFailedLabel);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

function init() {
  const state = parseState();
  const root = document.querySelector("[data-comparison-root]");
  if (!state || !root) {
    return;
  }

  const currentUrlState = parseComparisonUrlState(window.location.href);

  const labels = state.labels || {};
  requestFailedLabel = labels.requestFailed || requestFailedLabel;
  const saveErrorFallbackLabel = labels.saveErrorFallback || requestFailedLabel;
  const untitledLabel = labels.untitled || "";
  const statusText = root.querySelector("[data-comparison-status-text]");
  const statusActions = root.querySelector("[data-comparison-status-actions]");
  const feedback = root.querySelector("[data-comparison-feedback]");
  const volumeInput = root.querySelector("[data-comparison-volume]");
  const volumeValue = root.querySelector("[data-comparison-volume-value]");
  const rateInput = root.querySelector("[data-comparison-rate]");
  const rateValue = root.querySelector("[data-comparison-rate-value]");
  const materialControls = root.querySelector("[data-comparison-material-controls]");
  const setSummary = root.querySelector("[data-comparison-set-summary]");
  const materialPresetSelect = root.querySelector("[data-comparison-material-preset-select]");
  const learnerSessionsList = root.querySelector("[data-comparison-learner-sessions]");
  const nativeSessionsList = root.querySelector("[data-comparison-native-sessions]");
  const selectedSessionsList = root.querySelector("[data-comparison-selected-sessions]");
  const editItemsLink = root.querySelector("[data-comparison-edit-items]");
  const filterSearchInput = root.querySelector("[data-comparison-filter-search]");
  const levelSelect = root.querySelector("[data-comparison-filter-level-select]");
  const l1FilterSelect = root.querySelector("[data-comparison-filter-l1]");
  const genderFilterSelect = root.querySelector("[data-comparison-filter-gender]");
  const exposureFilterSelect = root.querySelector("[data-comparison-filter-exposure]");
  const activeFilters = root.querySelector("[data-comparison-active-filters]");
  const clearFiltersButton = root.querySelector("[data-comparison-clear-filters]");
  const filterCount = root.querySelector("[data-comparison-filter-count]");
  const matrixSummary = root.querySelector("[data-comparison-matrix-summary]");
  const matrixEmpty = root.querySelector("[data-comparison-matrix-empty]");
  const matrixWrap = root.querySelector("[data-comparison-matrix-wrap]");
  const matrixHead = root.querySelector("[data-comparison-matrix-head]");
  const matrixBody = root.querySelector("[data-comparison-matrix-body]");
  const saveDialog = root.querySelector("[data-comparison-save-dialog]");
  const saveHint = root.querySelector("[data-comparison-save-hint]");
  const saveForm = root.querySelector("[data-comparison-save-form]");
  const saveInput = root.querySelector("[data-comparison-save-input]");
  const saveError = root.querySelector("[data-comparison-save-error]");
  const saveCancel = root.querySelector("[data-comparison-save-cancel]");
  const saveConfirm = root.querySelector("[data-comparison-save-confirm]");

  const catalogLookup = new Map();
  Object.entries(state.catalogsByTask || {}).forEach(([taskKey, items]) => {
    for (const item of items) {
      catalogLookup.set(`${taskKey}:${item.item_id}`, item);
    }
  });

  const sessionLookup = new Map((state.sessionCatalog || []).map((session) => [session.sessionId, session]));
  const materialPresetLookup = new Map();
  const rateOptions = [0.5, 0.75, 1.0, 1.25, 1.5];
  const audio = new Audio();
  const clipCache = new Map();
  const DEFAULT_MATERIAL_OPTION = "__default__";
  const CURRENT_MATERIAL_OPTION = "__current__";
  let materialPresets = Array.isArray(state.materialPresets) ? state.materialPresets.slice() : [];

  let activeSet = null;
  let visibleViewTask = state.defaultViewTask || "wordlist";
  let playbackToken = 0;
  let activePlaybackCancel = null;
  let playbackState = "idle";
  let activeRowKey = null;
  let transientMessage = null;
  let feedbackState = null;
  let isSaving = false;
  let isImplicitDraft = false;
  let isExplicitMaterialSelection = Boolean(state.requestedSetId);
  let isBootstrappingWorkspace = Boolean(state.isAuthenticated && !state.requestedSetId);
  const filterState = {
    search: currentUrlState.filters.search || "",
    levels: new Set(currentUrlState.filters.levels || []),
    l1: currentUrlState.filters.l1 || "",
    gender: currentUrlState.filters.gender || "",
    exposure: currentUrlState.filters.exposure || "",
  };

  function currentFilterStateSnapshot() {
    return {
      search: filterState.search,
      levels: Array.from(filterState.levels),
      l1: filterState.l1,
      gender: filterState.gender,
      exposure: filterState.exposure,
    };
  }

  function hasRuntimeData() {
    return Boolean(state.hasRuntimeData ?? ((state.sessionCatalog || []).length > 0));
  }

  function setMaterialPresets(nextPresets) {
    materialPresets = Array.isArray(nextPresets) ? nextPresets.slice() : [];
    state.materialPresets = materialPresets;
    materialPresetLookup.clear();
    materialPresets.forEach((preset) => {
      materialPresetLookup.set(preset.presetId, preset);
    });
  }

  setMaterialPresets(materialPresets);

  function defaultSetItems() {
    return ["wordlist", "text"].flatMap((taskKey) =>
      Array.isArray(state.catalogsByTask && state.catalogsByTask[taskKey])
        ? state.catalogsByTask[taskKey].map((item) => ({ task: taskKey, item_id: item.item_id }))
        : []
    );
  }

  function itemKey(item) {
    return `${item.task}:${item.item_id}`;
  }

  function itemsMatch(leftItems, rightItems) {
    const leftKeys = new Set((leftItems || []).map(itemKey));
    const rightKeys = new Set((rightItems || []).map(itemKey));
    if (leftKeys.size !== rightKeys.size) {
      return false;
    }
    for (const key of leftKeys) {
      if (!rightKeys.has(key)) {
        return false;
      }
    }
    return true;
  }

  function itemsForPreset(presetId) {
    const preset = presetId ? materialPresetLookup.get(presetId) : null;
    return Array.isArray(preset && preset.items) ? preset.items : [];
  }

  function matchedPresetId(record = activeSet) {
    if (!record) {
      return null;
    }
    const matchingSavedSet = (state.materialPresets || []).find((preset) => preset.setId && preset.setId === record.set_id);
    if (matchingSavedSet) {
      return matchingSavedSet.presetId;
    }
    const explicitPresetId = record.source_preset_id;
    if (explicitPresetId && materialPresetLookup.has(explicitPresetId)) {
      return explicitPresetId;
    }
    for (const preset of state.materialPresets || []) {
      if (itemsMatch(record.items || [], preset.items || [])) {
        return preset.presetId;
      }
    }
    return null;
  }

  function requestedPresetId() {
    if (!state.requestedSetId) {
      return null;
    }
    const matched = (state.materialPresets || []).find((preset) => preset.setId && preset.setId === state.requestedSetId);
    return matched ? matched.presetId : null;
  }

  function resolveViewTaskForItems(items, preferredTask) {
    const availableTasks = new Set((items || []).map((item) => item.task));
    if (visibleViewTask !== "all" && availableTasks.has(visibleViewTask)) {
      return visibleViewTask;
    }
    if (preferredTask && availableTasks.has(preferredTask)) {
      return preferredTask;
    }
    if (availableTasks.has("wordlist")) {
      return "wordlist";
    }
    if (availableTasks.has("text")) {
      return "text";
    }
    return "all";
  }

  function normalizeWorkbenchState(record) {
    const nestedState = record && typeof record === "object" && record.workbench_state && typeof record.workbench_state === "object"
      ? record.workbench_state
      : {};
    const preferredTask = Object.prototype.hasOwnProperty.call(nestedState, "preferred_task")
      ? nestedState.preferred_task
      : null;
    const comparisonViewTask = typeof nestedState.comparison_view_task === "string"
      ? nestedState.comparison_view_task
      : "all";
    const sessions = Array.isArray(nestedState.sessions)
      ? nestedState.sessions
      : [];
    return {
      preferred_task: preferredTask,
      comparison_view_task: comparisonViewTask || "all",
      sessions,
    };
  }

  function normalizeSavedSetPreset(storedSet) {
    const label = (storedSet && storedSet.label) || untitledLabel;
    const workbenchState = normalizeWorkbenchState(storedSet);
    const items = Array.isArray(storedSet && storedSet.items)
      ? storedSet.items.map((item) => ({
        task: item.task,
        item_id: item.item_id,
      }))
      : [];
    const isCurated = storedSet && storedSet.visibility === "curated";
    return {
      presetId: isCurated ? storedSet.set_id : `saved:${storedSet.set_id}`,
      kind: isCurated ? "curated" : "custom",
      setId: storedSet.set_id,
      optionLabel: `${label} · ${isCurated ? (labels.stateCurated || "") : (labels.stateCustom || "")}`,
      label,
      preferredTask: workbenchState.comparison_view_task || workbenchState.preferred_task || resolveViewTaskForItems(items, null),
      taskSummary: "",
      items,
    };
  }

  function buildImplicitDefaultWorkspace() {
    return {
      set_id: null,
      visibility: "private",
      state: "implicit",
      label: null,
      items: defaultSetItems(),
      workbench_state: {
        comparison_view_task: visibleViewTask,
        preferred_task: visibleViewTask,
        sessions: [],
      },
    };
  }

  function applyPlaybackSettings() {
    const nextVolume = Number(volumeInput ? volumeInput.value : 100) / 100;
    const nextRateIndex = Number(rateInput ? rateInput.value : rateOptions.indexOf(1));
    const nextRate = rateOptions[nextRateIndex] || 1;
    audio.volume = Number.isFinite(nextVolume) ? nextVolume : 1;
    audio.playbackRate = Number.isFinite(nextRate) ? nextRate : 1;
    audio.defaultPlaybackRate = audio.playbackRate;
    if (volumeValue) {
      volumeValue.textContent = `${Math.round((Number.isFinite(nextVolume) ? nextVolume : 1) * 100)}%`;
    }
    if (rateValue) {
      rateValue.textContent = `${audio.playbackRate.toFixed(2)}×`;
    }
  }

  function rowKeyForItem(taskKey, itemId) {
    return `${taskKey}:${itemId}`;
  }

  function syncRowPlaybackButtons() {
    if (!matrixBody) {
      return;
    }
    const playLabel = labels.playRowLabel || "";
    const stopLabel = labels.stopLabel || playLabel;
    for (const button of matrixBody.querySelectorAll("[data-comparison-play-row]")) {
      const rowKey = button.dataset.comparisonPlayRow || "";
      const isActiveRow = playbackState === "playing" && rowKey && rowKey === activeRowKey;
      const nextLabel = isActiveRow ? stopLabel : playLabel;
      button.setAttribute("aria-label", nextLabel);
      button.setAttribute("title", nextLabel);
      button.setAttribute("aria-pressed", isActiveRow ? "true" : "false");
      button.dataset.playbackState = isActiveRow ? "playing" : "idle";
      button.innerHTML = iconSvg(isActiveRow ? "stop" : "play");
    }
  }

  function setRowPlaybackState(nextState, rowKey = null) {
    playbackState = nextState === "playing" ? "playing" : "idle";
    activeRowKey = playbackState === "playing" ? rowKey : null;
    syncRowPlaybackButtons();
  }

  function stopPlayback() {
    playbackToken += 1;
    const cancelCurrent = activePlaybackCancel;
    activePlaybackCancel = null;
    if (typeof cancelCurrent === "function") {
      cancelCurrent();
    }
    audio.pause();
    try {
      audio.currentTime = 0;
    } catch {
      // Some browsers reject currentTime changes before metadata is available.
    }
    audio.removeAttribute("src");
    audio.load();
    setRowPlaybackState("idle");
    clearActiveMatrixCell();
  }

  async function fetchClipUrl(href) {
    if (clipCache.has(href)) {
      return clipCache.get(href);
    }

    const response = await fetchWithAuth(href, {
      method: "HEAD",
      headers: { Accept: "audio/mpeg" },
    });
    const contentType = (response.headers.get("content-type") || "").toLowerCase();
    const contentDisposition = (response.headers.get("content-disposition") || "").toLowerCase();
    const contentLength = Number(response.headers.get("content-length") || "0");
    if (!response.ok) {
      throw new Error(response.statusText || requestFailedLabel);
    }
    if (contentDisposition.startsWith("attachment;")) {
      throw new Error(labels.clipUnavailable || requestFailedLabel);
    }
    if (!contentType.startsWith("audio/")) {
      throw new Error(labels.clipUnavailable || requestFailedLabel);
    }
    if (contentLength === 0) {
      throw new Error(labels.clipUnavailable || requestFailedLabel);
    }
    clipCache.set(href, href);
    return href;
  }

  async function playEntrySequence(entries, { rowKey = null } = {}) {
    if (!entries.length) {
      setFeedback(labels.workspaceNoMatches || requestFailedLabel, "error");
      return;
    }

    stopPlayback();
    const token = playbackToken;
    setRowPlaybackState("playing", rowKey);
    applyPlaybackSettings();
    for (const entry of entries) {
      if (token !== playbackToken) {
        return;
      }
      const clipHref = await fetchClipUrl(entry.href);
      if (token !== playbackToken) {
        return;
      }
      setActiveMatrixCell(entry.sessionId, entry.taskKey, entry.itemId);

      await new Promise((resolve, reject) => {
        let settled = false;
        const cleanup = () => {
          audio.removeEventListener("ended", onEnded);
          audio.removeEventListener("error", onError);
          audio.removeEventListener("pause", onPause);
          if (activePlaybackCancel === cancel) {
            activePlaybackCancel = null;
          }
        };

        const finish = (error = null) => {
          if (settled) {
            return;
          }
          settled = true;
          cleanup();
          if (error) {
            reject(error);
            return;
          }
          resolve();
        };

        const cancel = () => finish();
        const onEnded = () => finish();
        const onError = () => {
          clipCache.delete(entry.href);
          clearActiveMatrixCell();
          finish(new Error(labels.clipUnavailable || requestFailedLabel));
        };
        const onPause = () => {
          if (token !== playbackToken || audio.currentTime === 0) {
            finish();
          }
        };

        activePlaybackCancel = cancel;
        audio.addEventListener("ended", onEnded);
        audio.addEventListener("error", onError);
        audio.addEventListener("pause", onPause);
        audio.src = clipHref;
        audio.load();
        audio.currentTime = 0;
        audio.play().catch((error) => {
          finish(error);
        });
      });
    }

    if (token === playbackToken) {
      audio.pause();
      try {
        audio.currentTime = 0;
      } catch {
        // Some browsers reject currentTime changes before metadata is available.
      }
      setRowPlaybackState("idle");
      clearActiveMatrixCell();
    }
  }

  function redirectToLogin(extraQuery = {}) {
    const nextUrl = buildComparisonStateUrl(
      state.comparisonPageHref,
      currentComparisonUrlOptions({
        setId: Object.prototype.hasOwnProperty.call(extraQuery, "setId") ? extraQuery.setId : undefined,
        task: Object.prototype.hasOwnProperty.call(extraQuery, "task") ? extraQuery.task : undefined,
      }),
    );
    const loginUrl = new URL(state.loginHref, window.location.origin);
    loginUrl.searchParams.set("next", nextUrl);
    window.location.href = loginUrl.toString();
  }

  function lookupCatalogItem(taskKey, itemId) {
    return catalogLookup.get(`${taskKey}:${itemId}`) || null;
  }

  function enrichSet(record) {
    const workbenchState = normalizeWorkbenchState(record);
    const taskCounts = { wordlist: 0, text: 0 };
    const enrichedItems = (record.items || []).map((item) => {
      const catalogItem = lookupCatalogItem(item.task, item.item_id);
      taskCounts[item.task] = (taskCounts[item.task] || 0) + 1;
      return {
        ...item,
        taskLabel: state.taskLabels[item.task] || item.task,
        itemNumber: catalogItem ? catalogItem.item_number : item.item_id,
        text: catalogItem ? catalogItem.text : item.item_id,
        groupId: catalogItem ? catalogItem.group_id : null,
      };
    });

    const selectedSessions = (workbenchState.sessions || [])
      .map((entry) => sessionLookup.get(entry.session_id))
      .filter(Boolean);

    return {
      ...record,
      workbench_state: workbenchState,
      enrichedItems,
      taskCounts,
      selectedSessions,
    };
  }

  function applySet(record, options = {}) {
    if (Object.prototype.hasOwnProperty.call(options, "explicitMaterial")) {
      isExplicitMaterialSelection = Boolean(options.explicitMaterial);
    }
    activeSet = enrichSet(record);
    visibleViewTask = activeSet.workbench_state.comparison_view_task || visibleViewTask || "all";
    if (visibleViewTask === "all") {
      visibleViewTask = activeSet.taskCounts.wordlist > 0 ? "wordlist" : activeSet.taskCounts.text > 0 ? "text" : "all";
    }
    if (visibleViewTask !== "all" && !(activeSet.taskCounts[visibleViewTask] > 0)) {
      visibleViewTask = activeSet.enrichedItems.length ? (activeSet.taskCounts.wordlist > 0 ? "wordlist" : activeSet.taskCounts.text > 0 ? "text" : "all") : "all";
    }
    isImplicitDraft = Boolean(options.implicit && activeSet.state !== "saved");
    isBootstrappingWorkspace = false;
    transientMessage = null;
    syncUrl();
    render();
  }

  function currentComparisonUrlOptions(overrides = {}) {
    const activeSetId = activeSet && activeSet.set_id ? activeSet.set_id : state.requestedSetId || null;
    const nextSetId = shouldExposeComparisonSetId({
      activeSetId,
      requestedSetId: state.requestedSetId || null,
      isExplicitMaterialSelection,
      isImplicitDraft,
      isDefaultCompleteSet: isDefaultCompleteSet(),
      selectedSessionIds: selectedSessionIds(),
    })
      ? activeSetId
      : null;

    return {
      setId: Object.prototype.hasOwnProperty.call(overrides, "setId") ? overrides.setId : nextSetId,
      task: Object.prototype.hasOwnProperty.call(overrides, "task")
        ? overrides.task
        : (visibleViewTask && visibleViewTask !== "wordlist" && visibleViewTask !== "all" ? visibleViewTask : null),
      filters: Object.prototype.hasOwnProperty.call(overrides, "filters")
        ? overrides.filters
        : currentFilterStateSnapshot(),
    };
  }

  function syncUrl() {
    const nextUrl = buildComparisonStateUrl(state.comparisonPageHref, currentComparisonUrlOptions());
    window.history.replaceState({}, "", nextUrl);
  }

  function setFeedback(message, tone = "info") {
    feedbackState = message ? { message, tone } : null;
    if (!feedback) {
      return;
    }
    if (!feedbackState) {
      feedback.hidden = true;
      feedback.textContent = "";
      delete feedback.dataset.tone;
      return;
    }
    feedback.hidden = false;
    feedback.textContent = feedbackState.message;
    feedback.dataset.tone = feedbackState.tone;
  }

  function defaultComparisonSetLabel() {
    return labels.defaultSetLabel || "";
  }

  function defaultMaterialScopeLabel() {
    return visibleViewTask === "text"
      ? (labels.fullTextLabel || "")
      : (labels.fullListLabel || labels.defaultSetLabel || "");
  }

  function isDefaultCompleteSet() {
    if (!activeSet) {
      return false;
    }
    const expectedKeys = new Set(defaultSetItems().map((item) => `${item.task}:${item.item_id}`));
    const actualKeys = new Set((activeSet.items || []).map((item) => `${item.task}:${item.item_id}`));
    if (!expectedKeys.size || expectedKeys.size !== actualKeys.size) {
      return false;
    }
    for (const key of expectedKeys) {
      if (!actualKeys.has(key)) {
        return false;
      }
    }
    return true;
  }

  function currentSetDisplayName() {
    if (!activeSet || (!isExplicitMaterialSelection && (isImplicitDraft || isDefaultCompleteSet()))) {
      const requestedId = requestedPresetId();
      if (requestedId) {
        return materialPresetLookup.get(requestedId)?.optionLabel || defaultMaterialScopeLabel();
      }
      return defaultMaterialScopeLabel();
    }
    const matchedId = matchedPresetId();
    if (matchedId) {
      const matchedPreset = materialPresetLookup.get(matchedId);
      if (matchedPreset && matchedPreset.optionLabel) {
        return matchedPreset.optionLabel;
      }
    }
    if (activeSet.label) {
      return activeSet.label;
    }
    if (matchedId) {
      return labels.curatedMaterialLabel || materialPresetLookup.get(matchedId)?.label || matchedId;
    }
    return labels.customSetLabel || "";
  }

  function renderSetSummary() {
    if (!setSummary) {
      return;
    }
    setSummary.innerHTML = `<strong>${escapeHtml(currentSetDisplayName())}</strong>`;
  }

  function speakerCountLabel(count) {
    const singular = labels.speakerSingularLabel || "";
    const plural = labels.speakerPluralLabel || "";
    return `${count} ${count === 1 ? singular : plural}`;
  }

  function currentMaterialOptionValue() {
    if (!activeSet || (!isExplicitMaterialSelection && (isImplicitDraft || isDefaultCompleteSet()))) {
      const requestedId = requestedPresetId();
      if (requestedId) {
        return requestedId;
      }
      return DEFAULT_MATERIAL_OPTION;
    }
    const presetId = matchedPresetId();
    if (presetId) {
      return presetId;
    }
    return CURRENT_MATERIAL_OPTION;
  }

  function selectedSessionIds() {
    return activeSet ? (activeSet.workbench_state.sessions || []).map((entry) => entry.session_id) : [];
  }

  function isDraftRecord(record) {
    return Boolean(record && record.visibility === "private" && record.state === "draft");
  }

  async function ensureDraft() {
    if (isDraftRecord(activeSet)) {
      return activeSet;
    }
    if (!state.isAuthenticated) {
      redirectToLogin();
      throw new Error(labels.loginText || requestFailedLabel);
    }

    if (activeSet && activeSet.set_id) {
      const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(activeSet.set_id)}/private-copy`, {
        method: "POST",
        body: {
          lifecycle: "draft",
        },
      });
      applySet(payload.set, { implicit: false, explicitMaterial: isExplicitMaterialSelection });
      return activeSet;
    }

    const shouldPreserveDefaultMaterial = !isExplicitMaterialSelection && (!activeSet || isImplicitDraft || isDefaultCompleteSet());
    const defaultItems = defaultSetItems();
    const payload = await requestJson(state.createSetHref, {
      method: "POST",
      body: {
        corpus_language: state.languageSlug,
        workbench_state: {
          comparison_view_task: visibleViewTask,
        },
      },
    });
    let nextSet = payload.set;
    if (shouldPreserveDefaultMaterial && defaultItems.length && !itemsMatch(nextSet.items || [], defaultItems)) {
      const itemsPayload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(nextSet.set_id)}/items`, {
        method: "PUT",
        body: { items: defaultItems },
      });
      nextSet = itemsPayload.set;
    }
    applySet(nextSet, { implicit: shouldPreserveDefaultMaterial, explicitMaterial: !shouldPreserveDefaultMaterial });
    return activeSet;
  }

  async function loadRequestedSet() {
    if (!state.requestedSetId || !state.isAuthenticated) {
      return;
    }
    try {
      const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(state.requestedSetId)}`);
      applySet(payload.set, { implicit: false, explicitMaterial: true });
    } catch (error) {
      isBootstrappingWorkspace = false;
      transientMessage = error.message || saveErrorFallbackLabel;
      render();
    }
  }

  async function bootstrapDefaultWorkspace() {
    if (!state.isAuthenticated || state.requestedSetId || activeSet) {
      isBootstrappingWorkspace = false;
      return;
    }

    try {
      applySet(buildImplicitDefaultWorkspace(), { implicit: true });
    } catch (error) {
      isBootstrappingWorkspace = false;
      transientMessage = error.message || saveErrorFallbackLabel;
      render();
    }
  }

  function selectedSessions() {
    return activeSet ? activeSet.selectedSessions || [] : [];
  }

  function availableBaseSessions() {
    const selectedIds = new Set((activeSet && activeSet.workbench_state.sessions || []).map((entry) => entry.session_id));
    return (state.sessionCatalog || []).filter((session) => !selectedIds.has(session.sessionId));
  }

  function availableL1Values() {
    return Array.from(new Set((state.sessionCatalog || [])
      .map((session) => session.l1Value)
      .filter((value) => value && value !== "-")))
      .sort((left, right) => left.localeCompare(right));
  }

  function matchesBaseSessionFilters(session) {
    const needle = filterState.search.trim().toLowerCase();
    if (needle) {
      const haystack = `${session.personId || ""} ${session.sessionId || ""}`.toLowerCase();
      if (!haystack.includes(needle)) {
        return false;
      }
    }
    if (filterState.l1 && session.l1Value !== filterState.l1) {
      return false;
    }
    if (filterState.gender && session.genderKey !== filterState.gender) {
      return false;
    }
    if (filterState.exposure && session.targetCountryStayKey !== filterState.exposure) {
      return false;
    }
    return true;
  }

  function matchesLearnerLevelFilters(session) {
    if (!filterState.levels.size) {
      return true;
    }
    return Array.from(filterState.levels).some((level) => (session.levelValue || "").toUpperCase() === level);
  }

  function availableLearnerSessions() {
    return availableBaseSessions().filter((session) => !session.isNative && matchesBaseSessionFilters(session) && matchesLearnerLevelFilters(session));
  }

  function availableNativeSessions() {
    return availableBaseSessions().filter((session) => session.isNative && matchesBaseSessionFilters(session));
  }

  function orderedSelectedSessions() {
    return selectedSessions()
      .map((session, index) => ({ session, index }))
      .sort((left, right) => Number(left.session.isNative) - Number(right.session.isNative) || left.index - right.index)
      .map((entry) => entry.session);
  }

  function availableSessionCount() {
    return availableLearnerSessions().length + availableNativeSessions().length;
  }

  function hasActiveFilters() {
    return Boolean(
      filterState.search.trim()
      || filterState.levels.size
      || filterState.l1
      || filterState.gender
      || filterState.exposure
    );
  }

  function resetFilters() {
    filterState.search = "";
    filterState.levels.clear();
    filterState.l1 = "";
    filterState.gender = "";
    filterState.exposure = "";
  }

  function visibleItems() {
    if (!activeSet) {
      return [];
    }
    if (visibleViewTask === "all") {
      return activeSet.enrichedItems;
    }
    return activeSet.enrichedItems.filter((item) => item.task === visibleViewTask);
  }

  function buildItemClipHref(sessionId, taskKey, itemId) {
    const baseHref = state.playerHrefTemplate
      .replace("__SESSION__", encodeURIComponent(sessionId))
      .replace("__TASK__", encodeURIComponent(taskKey));
    return `${baseHref}/items/${encodeURIComponent(itemId)}.mp3`;
  }

  function buildItemDownloadHref(sessionId, taskKey, itemId) {
    return `${buildItemClipHref(sessionId, taskKey, itemId)}?download=1`;
  }

  function firstCompareSessionId(taskKey, primarySessionId) {
    return selectedSessions()
      .filter((session) => session.sessionId !== primarySessionId)
      .find((session) => Array.isArray(session.availableTasks) && session.availableTasks.includes(taskKey))?.sessionId || null;
  }

  function buildPlayerHref(taskKey, sessionId, focusItemId = null) {
    if (!activeSet || !taskKey || !sessionId) {
      return null;
    }
    const baseHref = state.playerHrefTemplate
      .replace("__SESSION__", encodeURIComponent(sessionId))
      .replace("__TASK__", encodeURIComponent(taskKey));
    return buildQueryUrl(baseHref, {
      source: "comparison",
      set_id: activeSet.set_id,
      compare_session: firstCompareSessionId(taskKey, sessionId),
      focus_item: focusItemId || null,
    });
  }

  function sessionSupportsItem(session, item) {
    const itemIds = (session && session.availableItemIdsByTask && session.availableItemIdsByTask[item.task]) || [];
    return itemIds.includes(item.item_id);
  }

  function clearActiveMatrixCell() {
    if (!matrixBody) {
      return;
    }
    for (const cell of matrixBody.querySelectorAll(".pm-comparison-matrix__cell.is-active")) {
      cell.classList.remove("is-active");
    }
  }

  function setActiveMatrixCell(sessionId, taskKey, itemId) {
    clearActiveMatrixCell();
    if (!matrixBody || !sessionId || !taskKey || !itemId) {
      return;
    }
    const nextCell = Array.from(matrixBody.querySelectorAll("[data-comparison-matrix-cell]"))
      .find((cell) => cell.dataset.comparisonMatrixCell === `${sessionId}|${taskKey}|${itemId}`);
    if (nextCell) {
      nextCell.classList.add("is-active");
    }
  }

  function syncMatrixStubLineState() {
    if (!matrixBody) {
      return;
    }

    for (const stub of matrixBody.querySelectorAll(".pm-comparison-matrix__item")) {
      const text = stub.querySelector(".pm-comparison-item__text");
      if (!text) {
        stub.classList.remove("is-single-line", "is-multi-line");
        continue;
      }

      const computedStyle = window.getComputedStyle(text);
      const lineHeight = Number.parseFloat(computedStyle.lineHeight);
      const measuredHeight = text.getBoundingClientRect().height;
      const isMultiLine = Number.isFinite(lineHeight)
        ? measuredHeight > (lineHeight * 1.45)
        : measuredHeight > 24;

      stub.classList.toggle("is-multi-line", isMultiLine);
      stub.classList.toggle("is-single-line", !isMultiLine);
    }
  }

  function speakerMetaMarkup(session) {
    if (session.isNative) {
      return session.standardVarietyValue
        ? `<span class="pm-comparison-speaker-badge pm-comparison-speaker-badge--native-detail">${escapeHtml(session.standardVarietyValue)}</span>`
        : "";
    }

    const levelBadgeText = session.levelValue && session.levelValue !== "-"
      ? `${labels.selfPlacementPrefix ? labels.selfPlacementPrefix + " " : ""}${session.levelValue}`
      : "";
    return [
      levelBadgeText
        ? `<span class="pm-comparison-speaker-badge pm-comparison-speaker-badge--level pm-comparison-speaker-badge--${escapeHtml((session.levelValue || "").toLowerCase())}">${escapeHtml(levelBadgeText)}</span>`
        : "",
      session.l1BadgeLabel
        ? `<span class="pm-comparison-speaker-badge pm-comparison-speaker-badge--detail">${escapeHtml(session.l1BadgeLabel)}</span>`
        : "",
    ].join("");
  }

  function speakerCardMarkup(session, { isSelectedList = false, actionLabel = "", matrix = false } = {}) {
    const bodyMarkup = `
      <span class="pm-comparison-speaker-row__body">
        <span class="pm-comparison-speaker-row__title">${escapeHtml(session.personId)}</span>
        <span class="pm-comparison-speaker-row__meta">${speakerMetaMarkup(session)}</span>
      </span>
    `;

    if (matrix) {
      return `
        <div class="pm-comparison-speaker-row pm-comparison-speaker-row--matrix" title="${escapeHtml(session.personId)} · ${escapeHtml(session.sessionId)}">
          ${bodyMarkup}
        </div>
      `;
    }

    return `
      <button
        type="button"
        class="pm-comparison-speaker-row${isSelectedList ? " is-selected pm-comparison-speaker-row--selected" : ""}"
        data-comparison-session-toggle="${escapeHtml(session.sessionId)}"
        aria-pressed="${isSelectedList ? "true" : "false"}"
        aria-label="${escapeHtml(actionLabel)}: ${escapeHtml(session.personId)}"
        title="${escapeHtml(session.personId)} · ${escapeHtml(session.sessionId)}"
      >
        ${bodyMarkup}
        <span class="pm-comparison-speaker-row__indicator" aria-hidden="true">${isSelectedList ? iconSvg("close") : ""}</span>
      </button>
    `;
  }

  function setStatus(title, text, actions = []) {
    void title;
    if (statusText) {
      statusText.hidden = !text;
      statusText.textContent = text;
    }
    if (!statusActions) {
      return;
    }
    statusActions.innerHTML = "";
    for (const action of actions) {
      const element = document.createElement(action.href ? "a" : "button");
      element.className = action.className || "pm-action-button pm-action-button--secondary pm-action-button--medium";
      element.textContent = action.label;
      if (action.href) {
        element.href = action.href;
      } else {
        element.type = "button";
        element.dataset.comparisonAction = action.action;
      }
      statusActions.append(element);
    }
  }

  function setDialogError(message) {
    if (!saveError) {
      return;
    }
    if (!message) {
      saveError.hidden = true;
      saveError.textContent = "";
      return;
    }
    saveError.hidden = false;
    saveError.textContent = message;
  }

  function setSavePending(pending) {
    isSaving = pending;
    if (saveInput) {
      saveInput.disabled = pending;
    }
    if (saveCancel) {
      saveCancel.disabled = pending;
    }
    if (saveConfirm) {
      saveConfirm.disabled = pending;
    }
  }

  function closeSaveDialog() {
    setDialogError("");
    setSavePending(false);
    if (!saveDialog) {
      return;
    }
    if (typeof saveDialog.close === "function") {
      saveDialog.close();
      return;
    }
    saveDialog.removeAttribute("open");
  }

  function openSaveDialog() {
    if (!saveDialog || !saveInput || !activeSet) {
      return;
    }
    setDialogError("");
    setSavePending(false);
    if (saveHint) {
      saveHint.textContent = labels.saveHint || "";
    }
    saveInput.value = activeSet.suggested_save_label || activeSet.label || "";
    if (typeof saveDialog.showModal === "function") {
      saveDialog.showModal();
    } else {
      saveDialog.setAttribute("open", "open");
    }
    window.requestAnimationFrame(() => {
      saveInput.focus();
      saveInput.select();
    });
  }

  async function saveAsNewSet() {
    if (!activeSet || !saveInput) {
      return;
    }

    const label = (saveInput.value || "").trim();
    if (!label) {
      setDialogError(labels.saveValidationError || requestFailedLabel);
      return;
    }

    setSavePending(true);
    try {
      const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(activeSet.set_id)}/save-as`, {
        method: "POST",
        body: { label },
      });
      applySet(payload.set);
      closeSaveDialog();
      setFeedback(`${labels.saveSuccessPrefix || ""} ${label}`, "success");
      render();
    } catch (error) {
      setSavePending(false);
      if (error.status === 401) {
        closeSaveDialog();
        redirectToLogin({ setId: activeSet.set_id, task: visibleViewTask !== "all" ? visibleViewTask : null });
        return;
      }
      if (error.status === 400) {
        setDialogError((error.payload && error.payload.error) || labels.saveValidationError || requestFailedLabel);
        return;
      }
      setDialogError((error.payload && error.payload.error) || labels.saveBackendError || saveErrorFallbackLabel);
    }
  }

  function renderStatus() {
    if (transientMessage) {
      setStatus(labels.statusTitle || "", transientMessage, []);
      return;
    }
    if (isBootstrappingWorkspace) {
      setStatus(labels.materialLoadingTitle || labels.emptyTitle || "", labels.materialLoadingText || labels.emptyText || "", []);
      return;
    }
    if (!activeSet && state.requestedSetId && state.isAuthenticated) {
      setStatus(labels.statusTitle || "", labels.loadingSet || "", []);
      return;
    }
    setStatus("", "", []);
  }

  function renderMaterialControls() {
    if (!materialControls) {
      return;
    }
    const availableTasks = ["wordlist", "text"];
    materialControls.innerHTML = availableTasks
      .map((entry) => {
        const isCurrent = entry === visibleViewTask;
        const isDisabled = Boolean(activeSet && !(activeSet.taskCounts[entry] > 0) && !isCurrent);
        return `
        <button
          type="button"
          class="pm-material-choice${isCurrent ? " is-current" : ""}${isDisabled ? " is-disabled" : ""}"
          data-comparison-view-filter="${escapeHtml(entry)}"
          ${isCurrent || isDisabled ? "disabled" : ""}
          aria-pressed="${isCurrent ? "true" : "false"}"
        >${escapeHtml(state.taskLabels[entry] || entry)}</button>
      `;
      })
      .join("");
  }

  function renderFilterControls() {
    if (filterSearchInput) {
      filterSearchInput.value = filterState.search;
    }

    if (levelSelect) {
      levelSelect.value = Array.from(filterState.levels)[0] || "";
    }

    if (l1FilterSelect) {
      l1FilterSelect.innerHTML = [
        `<option value="">${escapeHtml(labels.l1FilterLabel || "")}</option>`,
        ...availableL1Values().map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`),
      ].join("");
      l1FilterSelect.value = filterState.l1;
    }

    if (genderFilterSelect) {
      const genderOptions = Array.from(new Map((state.sessionCatalog || [])
        .filter((session) => session.genderKey && session.genderKey !== "unknown")
        .map((session) => [session.genderKey, session.genderLabel]))).sort((left, right) => String(left[1]).localeCompare(String(right[1])));
      genderFilterSelect.innerHTML = [
        `<option value="">${escapeHtml(labels.filterAllLabel || "")}</option>`,
        ...genderOptions.map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`),
      ].join("");
      genderFilterSelect.value = filterState.gender;
    }

    if (exposureFilterSelect) {
      exposureFilterSelect.innerHTML = [
        `<option value="">${escapeHtml(labels.filterAllLabel || "")}</option>`,
        `<option value="yes">${escapeHtml(labels.exposureYesLabel || "")}</option>`,
        `<option value="no">${escapeHtml(labels.exposureNoLabel || "")}</option>`,
      ].join("");
      exposureFilterSelect.value = filterState.exposure;
    }

    if (filterCount) {
      filterCount.textContent = speakerCountLabel(availableSessionCount());
    }

    if (activeFilters) {
      const chips = [];
      for (const level of filterState.levels) {
        chips.push({ key: `level:${level}`, label: `${labels.selfPlacementPrefix || ""} ${level}`.trim() });
      }
      if (filterState.l1) {
        chips.push({ key: "l1", label: `${labels.l1ShortLabel || ""}: ${filterState.l1}` });
      }
      if (filterState.gender && genderFilterSelect) {
        const selected = genderFilterSelect.selectedOptions[0];
        chips.push({ key: "gender", label: selected ? selected.textContent || filterState.gender : filterState.gender });
      }
      if (filterState.exposure) {
        chips.push({
          key: "exposure",
          label: filterState.exposure === "yes"
            ? (labels.exposureYesLabel || "")
            : (labels.exposureNoLabel || ""),
        });
      }
      if (filterState.search.trim()) {
        chips.push({ key: "search", label: filterState.search.trim() });
      }
      activeFilters.innerHTML = chips.map((chip) => `
        <button type="button" class="pm-filter-chip pm-comparison-active-filter" data-comparison-remove-filter="${escapeHtml(chip.key)}">
          ${escapeHtml(chip.label)} <span aria-hidden="true">×</span>
        </button>
      `).join("");
    }

    if (clearFiltersButton) {
      clearFiltersButton.hidden = !hasActiveFilters();
      clearFiltersButton.style.display = hasActiveFilters() ? "" : "none";
    }
  }

  function renderMaterialPresetControl() {
    if (!materialPresetSelect) {
      return;
    }

    const options = [
      `<option value="${DEFAULT_MATERIAL_OPTION}">${escapeHtml(defaultMaterialScopeLabel())}</option>`,
    ];

    if (currentMaterialOptionValue() === CURRENT_MATERIAL_OPTION) {
      options.push(`<option value="${CURRENT_MATERIAL_OPTION}">${escapeHtml(currentSetDisplayName())}</option>`);
    }

    for (const preset of materialPresets) {
      options.push(`<option value="${escapeHtml(preset.presetId)}">${escapeHtml(preset.optionLabel || preset.label)}</option>`);
    }

    materialPresetSelect.innerHTML = options.join("");
    materialPresetSelect.value = currentMaterialOptionValue();
    materialPresetSelect.disabled = false;
  }

  async function updateMaterialSelection({ presetId = null } = {}) {
    if (!state.isAuthenticated) {
      redirectToLogin({ setId: activeSet && activeSet.set_id, task: visibleViewTask !== "all" ? visibleViewTask : null });
      throw new Error(labels.loginText || requestFailedLabel);
    }

    const ensuredSet = await ensureDraft();
    const nextItems = presetId ? itemsForPreset(presetId) : defaultSetItems();
    const nextViewTask = resolveViewTaskForItems(nextItems, presetId ? materialPresetLookup.get(presetId)?.preferredTask : visibleViewTask);

    let nextSet = ensuredSet;
    if (!itemsMatch(ensuredSet.items || [], nextItems)) {
      const itemsPayload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(ensuredSet.set_id)}/items`, {
        method: "PUT",
        body: { items: nextItems },
      });
      nextSet = itemsPayload.set;
    }

    if ((normalizeWorkbenchState(nextSet).comparison_view_task || "all") !== nextViewTask) {
      const metadataPayload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(nextSet.set_id)}`, {
        method: "PATCH",
        body: {
          workbench_state: {
            comparison_view_task: nextViewTask,
          },
        },
      });
      nextSet = metadataPayload.set;
    }

    const isDefaultMaterialSelection = !presetId && itemsMatch(nextItems, defaultSetItems());
    const shouldUseImplicitDraft = !state.requestedSetId && nextSet.state !== "saved" && isDefaultMaterialSelection;
    applySet(nextSet, { implicit: shouldUseImplicitDraft, explicitMaterial: !isDefaultMaterialSelection });
  }

  function renderSessionList(target, sessions, { isSelectedList = false, actionLabel, emptyText } = {}) {
    if (!target) {
      return;
    }
    if (!sessions.length) {
      target.innerHTML = `<li class="pm-comparison-session-list__empty">${escapeHtml(emptyText)}</li>`;
      return;
    }

    target.innerHTML = sessions
      .map((session) => `
        <li>
          ${speakerCardMarkup(session, { isSelectedList, actionLabel })}
        </li>
      `)
      .join("");
  }

  function renderSessions() {
    const noDataText = !hasRuntimeData() ? (labels.noDataText || "") : null;
    renderSessionList(
      learnerSessionsList,
      availableLearnerSessions(),
      {
        isSelectedList: false,
        actionLabel: labels.addSessionLabel || "",
        emptyText: noDataText || labels.availableEmptyFiltered || "",
      },
    );
    renderSessionList(
      nativeSessionsList,
      availableNativeSessions(),
      {
        isSelectedList: false,
        actionLabel: labels.addSessionLabel || "",
        emptyText: noDataText || labels.availableEmptyFiltered || "",
      },
    );
    renderSessionList(
      selectedSessionsList,
      orderedSelectedSessions(),
      {
        isSelectedList: true,
        actionLabel: labels.removeSessionLabel || "",
        emptyText: noDataText || labels.selectedEmpty || labels.workspaceEmptySessions || "",
      },
    );
  }

  function renderMaterialActions() {
    renderMaterialPresetControl();
  }

  function renderMatrix() {
    if (!matrixSummary || !matrixEmpty || !matrixWrap || !matrixHead || !matrixBody) {
      return;
    }
    if (playbackState === "playing") {
      stopPlayback();
    }

    const items = visibleItems();
    const sessions = selectedSessions();
    if (!hasRuntimeData()) {
      matrixSummary.textContent = labels.materialText || "";
      matrixEmpty.textContent = labels.noDataText || "";
      matrixWrap.hidden = true;
      return;
    }
    if (!activeSet) {
      matrixSummary.textContent = labels.materialText || "";
      matrixEmpty.textContent = labels.workspaceEmptyItems || "";
      matrixWrap.hidden = true;
      return;
    }

    matrixSummary.textContent = `${state.taskLabels[visibleViewTask] || labels.itemsTitle || ""} · ${items.length} ${labels.workspaceItems || ""} · ${speakerCountLabel(sessions.length)}`;
    if (!items.length) {
      matrixEmpty.textContent = labels.workspaceNoRows || "";
      matrixWrap.hidden = true;
      return;
    }
    if (!sessions.length) {
      matrixEmpty.textContent = labels.selectedEmpty || labels.workspaceEmptySessions || "";
      matrixWrap.hidden = true;
      return;
    }

    matrixEmpty.textContent = "";
    matrixWrap.hidden = false;
    matrixHead.innerHTML = `
      <tr>
        <th class="pm-comparison-matrix__stub" scope="col">${escapeHtml(labels.itemsTitle || "")}</th>
        ${sessions.map((session) => `
          <th class="pm-comparison-matrix__session" scope="col" title="${escapeHtml(session.sessionId)}">
            ${speakerCardMarkup(session, { matrix: true })}
          </th>
        `).join("")}
      </tr>
    `;
    matrixBody.innerHTML = items
      .map((item) => {
        const rowEntries = sessions
          .filter((session) => sessionSupportsItem(session, item))
          .map((session) => ({
            href: buildItemClipHref(session.sessionId, item.task, item.item_id),
            label: `${labels.playbackSpeakerPrefix || ""} ${session.personId} · ${item.itemNumber}`,
            sessionId: session.sessionId,
            taskKey: item.task,
            itemId: item.item_id,
          }));
        return `
          <tr>
            <th class="pm-comparison-matrix__item" scope="row">
              <div class="pm-comparison-matrix__item-inner">
                <div class="pm-comparison-matrix__item-header">
                  <div>
                  <div class="pm-comparison-item__meta-row">
                    <span class="pm-comparison-item__number">${escapeHtml(item.itemNumber)}</span>
                  </div>
                  <p class="pm-comparison-item__text pm-item-content-text pm-item-content-text--compare">${escapeHtml(item.text)}</p>
                </div>
                  ${rowEntries.length ? `<button type="button" class="pm-player-icon-button pm-comparison-icon-button pm-comparison-icon-button--primary pm-comparison-matrix__row-play" data-comparison-play-row="${escapeHtml(rowKeyForItem(item.task, item.item_id))}" aria-label="${escapeHtml(labels.playRowLabel || "")}" title="${escapeHtml(labels.playRowLabel || "")}" aria-pressed="false" data-playback-state="idle">${iconSvg("play")}</button>` : ""}
                </div>
              </div>
            </th>
            ${sessions.map((session) => {
              if (!sessionSupportsItem(session, item)) {
                return `<td class="pm-comparison-matrix__cell pm-comparison-matrix__cell--missing"><span class="pm-comparison-matrix__missing" aria-label="${escapeHtml(labels.clipMissing || "")}" title="${escapeHtml(labels.clipMissing || "")}">-</span></td>`;
              }
              const clipHref = buildItemClipHref(session.sessionId, item.task, item.item_id);
              const downloadHref = buildItemDownloadHref(session.sessionId, item.task, item.item_id);
              return `
                <td class="pm-comparison-matrix__cell" data-comparison-matrix-cell="${escapeHtml(session.sessionId)}|${escapeHtml(item.task)}|${escapeHtml(item.item_id)}">
                  <div class="pm-comparison-matrix__cell-actions">
                    <button type="button" class="pm-player-icon-button pm-comparison-icon-button pm-comparison-icon-button--primary" data-comparison-play-cell="${escapeHtml(session.sessionId)}|${escapeHtml(item.task)}|${escapeHtml(item.item_id)}|${escapeHtml(item.itemNumber)}" aria-label="${escapeHtml(labels.playClipLabel || "")}" title="${escapeHtml(labels.playClipLabel || "")}">${iconSvg("play")}</button>
                    <a class="pm-player-icon-button pm-comparison-icon-button pm-comparison-icon-button--secondary" href="${escapeHtml(downloadHref)}" download aria-label="${escapeHtml(labels.downloadClip || "")}" title="${escapeHtml(labels.downloadClip || "")}">${iconSvg("download")}</a>
                  </div>
                </td>
              `;
            }).join("")}
          </tr>
        `;
      })
      .join("");

    syncRowPlaybackButtons();
    window.requestAnimationFrame(() => {
      syncMatrixStubLineState();
    });
  }

  function render() {
    renderStatus();
    setFeedback(feedbackState && feedbackState.message, feedbackState && feedbackState.tone);
    renderMaterialControls();
    renderMaterialPresetControl();
    renderFilterControls();
    renderSessions();
    renderMaterialActions();
    renderMatrix();
  }

  async function updateSessions(nextSessionIds) {
    const ensuredSet = await ensureDraft();
    const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(ensuredSet.set_id)}/sessions`, {
      method: "PUT",
      body: {
        sessions: nextSessionIds.map((sessionId) => ({ session_id: sessionId })),
      },
    });
    applySet(payload.set);
  }

  async function updateViewTask(nextViewTask) {
    visibleViewTask = nextViewTask;
    syncUrl();
    render();
    if (!activeSet && !state.isAuthenticated) {
      return;
    }

    const ensuredSet = await ensureDraft();

    const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(ensuredSet.set_id)}`, {
      method: "PATCH",
      body: {
        workbench_state: {
          comparison_view_task: nextViewTask,
        },
      },
    });
    applySet(payload.set);
  }

  root.addEventListener("click", async (event) => {
    const createAction = event.target.closest("[data-comparison-action='create'], [data-comparison-create]");
    if (createAction) {
      event.preventDefault();
      try {
        await ensureDraft();
      } catch (error) {
        transientMessage = error.message || saveErrorFallbackLabel;
        render();
      }
      return;
    }

    const filterButton = event.target.closest("[data-comparison-view-filter]");
    if (filterButton) {
      event.preventDefault();
      const nextViewTask = filterButton.dataset.comparisonViewFilter || "all";
      try {
        await updateViewTask(nextViewTask);
      } catch (error) {
        transientMessage = error.message || saveErrorFallbackLabel;
        render();
      }
      return;
    }

    const sessionToggleButton = event.target.closest("[data-comparison-session-toggle]");
    if (sessionToggleButton) {
      event.preventDefault();
      const sessionId = sessionToggleButton.dataset.comparisonSessionToggle;
      if (!sessionId) {
        return;
      }
      try {
        const currentIds = activeSet ? (activeSet.workbench_state.sessions || []).map((entry) => entry.session_id) : [];
        if (currentIds.includes(sessionId)) {
          await updateSessions(currentIds.filter((id) => id !== sessionId));
        } else {
          await updateSessions([...currentIds, sessionId]);
        }
      } catch (error) {
        transientMessage = error.message || saveErrorFallbackLabel;
        render();
      }
      return;
    }


    const removeFilterButton = event.target.closest("[data-comparison-remove-filter]");
    if (removeFilterButton) {
      event.preventDefault();
      const key = removeFilterButton.dataset.comparisonRemoveFilter || "";
      if (key === "search") {
        filterState.search = "";
      } else if (key === "l1") {
        filterState.l1 = "";
      } else if (key === "gender") {
        filterState.gender = "";
      } else if (key === "exposure") {
        filterState.exposure = "";
      } else if (key.startsWith("level:")) {
        filterState.levels.delete(key.split(":")[1] || "");
      }
      syncUrl();
      render();
      return;
    }

    const clearFiltersAction = event.target.closest("[data-comparison-clear-filters]");
    if (clearFiltersAction) {
      event.preventDefault();
      resetFilters();
      syncUrl();
      render();
      return;
    }

    const playCellButton = event.target.closest("[data-comparison-play-cell]");
    if (playCellButton) {
      event.preventDefault();
      const rawValue = playCellButton.dataset.comparisonPlayCell || "";
      const [sessionId, taskKey, itemId, itemNumber] = rawValue.split("|");
      if (!sessionId || !taskKey || !itemId) {
        return;
      }
      try {
        const session = sessionLookup.get(sessionId);
        await playEntrySequence([
          {
            href: buildItemClipHref(sessionId, taskKey, itemId),
            label: `${labels.playbackSpeakerPrefix || ""} ${(session && session.personId) || sessionId} · ${itemNumber || itemId}`,
            sessionId,
            taskKey,
            itemId,
          },
        ]);
      } catch (error) {
        stopPlayback();
        setFeedback(error.message || saveErrorFallbackLabel, "error");
      }
      return;
    }

    const playRowButton = event.target.closest("[data-comparison-play-row]");
    if (playRowButton) {
      event.preventDefault();
      const rawValue = playRowButton.dataset.comparisonPlayRow || "";
      if (playbackState === "playing" && activeRowKey === rawValue) {
        stopPlayback();
        return;
      }
      const [taskKey, itemId] = rawValue.split(":");
      const item = activeSet && activeSet.enrichedItems.find((entry) => entry.task === taskKey && entry.item_id === itemId);
      if (!item) {
        return;
      }
      const entries = selectedSessions()
        .filter((session) => sessionSupportsItem(session, item))
        .map((session) => ({
          href: buildItemClipHref(session.sessionId, taskKey, itemId),
          label: `${labels.playbackRowPrefix || ""} ${item.itemNumber} · ${session.personId}`,
          sessionId: session.sessionId,
          taskKey,
          itemId,
        }));
      try {
        await playEntrySequence(entries, { rowKey: rawValue });
      } catch (error) {
        stopPlayback();
        setFeedback(error.message || saveErrorFallbackLabel, "error");
      }
    }
  });

  window.addEventListener("resize", () => {
    window.requestAnimationFrame(() => {
      syncMatrixStubLineState();
    });
  });

  if (volumeInput) {
    volumeInput.addEventListener("input", applyPlaybackSettings);
  }
  if (filterSearchInput) {
    filterSearchInput.addEventListener("input", () => {
      filterState.search = filterSearchInput.value || "";
      syncUrl();
      render();
    });
  }
  if (materialPresetSelect) {
    materialPresetSelect.addEventListener("change", async () => {
      const nextValue = materialPresetSelect.value || DEFAULT_MATERIAL_OPTION;
      if (nextValue === CURRENT_MATERIAL_OPTION) {
        renderMaterialPresetControl();
        return;
      }
      try {
        await updateMaterialSelection({ presetId: nextValue === DEFAULT_MATERIAL_OPTION ? null : nextValue });
      } catch (error) {
        transientMessage = error.message || saveErrorFallbackLabel;
        render();
      }
    });
  }
  if (levelSelect) {
    levelSelect.addEventListener("change", () => {
      const value = levelSelect.value || "";
      filterState.levels = new Set(value ? [value] : []);
      syncUrl();
      render();
    });
  }
  if (l1FilterSelect) {
    l1FilterSelect.addEventListener("change", () => {
      filterState.l1 = l1FilterSelect.value || "";
      syncUrl();
      render();
    });
  }
  if (genderFilterSelect) {
    genderFilterSelect.addEventListener("change", () => {
      filterState.gender = genderFilterSelect.value || "";
      syncUrl();
      render();
    });
  }
  if (exposureFilterSelect) {
    exposureFilterSelect.addEventListener("change", () => {
      filterState.exposure = exposureFilterSelect.value || "";
      syncUrl();
      render();
    });
  }
  if (rateInput) {
    rateInput.addEventListener("input", applyPlaybackSettings);
    rateInput.addEventListener("change", applyPlaybackSettings);
  }
  if (rateInput) {
    rateInput.value = String(Math.max(rateOptions.indexOf(1), 0));
  }
  if (saveCancel) {
    saveCancel.addEventListener("click", () => {
      if (!isSaving) {
        closeSaveDialog();
      }
    });
  }
  if (saveDialog) {
    saveDialog.addEventListener("cancel", (event) => {
      if (isSaving) {
        event.preventDefault();
        return;
      }
      closeSaveDialog();
    });
  }
  if (saveForm) {
    saveForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      await saveAsNewSet();
    });
  }
  applyPlaybackSettings();
  render();
  if (state.requestedSetId) {
    loadRequestedSet();
  } else {
    bootstrapDefaultWorkspace();
  }

  window.addEventListener("beforeunload", () => {
    stopPlayback();
    clipCache.clear();
  });
  window.addEventListener("pagehide", () => {
    stopPlayback();
  });
}

init();
