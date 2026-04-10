import { getCsrfToken } from "../api.js";
import { fetchWithAuth } from "../modules/auth/refresh.js";

function parseState() {
  const element = document.getElementById("pm-phenomena-state");
  if (!element) {
    return null;
  }

  try {
    const parsed = JSON.parse(element.textContent || "{}");
    return parsed && parsed.catalogsByTask ? parsed : null;
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
    const error = new Error((payload && payload.error) || response.statusText || "Request failed");
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

function init() {
  const state = parseState();
  const root = document.querySelector("[data-phenomena-root]");
  if (!state || !root) {
    return;
  }

  const labels = state.labels || {};
  const statusHeading = root.querySelector("[data-phenomena-status-heading]");
  const statusMeta = root.querySelector("[data-phenomena-status-meta]");
  const statusText = root.querySelector("[data-phenomena-status-text]");
  const statusActions = root.querySelector("[data-phenomena-status-actions]");
  const feedback = root.querySelector("[data-phenomena-feedback]");
  const launcherPanel = root.querySelector("[data-phenomena-launcher]");
  const itemsPanel = root.querySelector("[data-phenomena-items-panel]");
  const itemsSummary = root.querySelector("[data-phenomena-items-summary]");
  const itemsList = root.querySelector("[data-phenomena-items]");
  const browserPanel = root.querySelector("[data-phenomena-browser-panel]");
  const browserSummary = root.querySelector("[data-phenomena-browser-summary]");
  const browserResults = root.querySelector("[data-phenomena-browser-results]");
  const browserTaskSelect = root.querySelector("[data-phenomena-browser-task]");
  const searchInput = root.querySelector("[data-phenomena-search]");
  const launchTaskSelect = root.querySelector("[data-phenomena-launch-task]");
  const launchSessionSelect = root.querySelector("[data-phenomena-launch-session]");
  const comparisonLink = root.querySelector("[data-phenomena-comparison-link]");
  const playerLink = root.querySelector("[data-phenomena-player-link]");
  const playerNote = root.querySelector("[data-phenomena-player-note]");
  const saveDialog = root.querySelector("[data-phenomena-save-dialog]");
  const saveHint = root.querySelector("[data-phenomena-save-hint]");
  const saveForm = root.querySelector("[data-phenomena-save-form]");
  const saveInput = root.querySelector("[data-phenomena-save-input]");
  const saveError = root.querySelector("[data-phenomena-save-error]");
  const saveCancel = root.querySelector("[data-phenomena-save-cancel]");
  const saveConfirm = root.querySelector("[data-phenomena-save-confirm]");
  const presetButtons = Array.from(root.querySelectorAll("[data-phenomena-open-preset]"));
  const presetCards = Array.from(root.querySelectorAll("[data-phenomena-preset-card]"));

  const catalogLookup = new Map();
  Object.entries(state.catalogsByTask || {}).forEach(([taskKey, items]) => {
    for (const item of items) {
      catalogLookup.set(`${taskKey}:${item.item_id}`, item);
    }
  });

  const presetLookup = new Map((state.presets || []).map((preset) => [preset.presetId, preset]));
  let activeSet = null;
  let launchTask = state.requestedTask || "wordlist";
  let browserTask = state.requestedTask || "wordlist";
  let searchTerm = "";
  let transientMessage = null;
  let feedbackState = null;
  let isSaving = false;

  function redirectToLogin(extraQuery = {}) {
    const nextUrl = buildQueryUrl(state.phenomenaPageHref, {
      preset_id: extraQuery.presetId || (activeSet && activeSet.source_preset_id) || state.requestedPresetId || null,
      set_id: extraQuery.setId || (activeSet && activeSet.set_id) || state.requestedSetId || null,
      task: extraQuery.task || launchTask || state.requestedTask || null,
    });
    const loginUrl = new URL(state.loginHref, window.location.origin);
    loginUrl.searchParams.set("next", nextUrl);
    window.location.href = loginUrl.toString();
  }

  function lookupCatalogItem(task, itemId) {
    return catalogLookup.get(`${task}:${itemId}`) || null;
  }

  function enrichSet(record) {
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
    return { ...record, enrichedItems, taskCounts };
  }

  function applySet(record) {
    activeSet = enrichSet(record);
    state.requestedSetId = activeSet.set_id;
    state.requestedPresetId = activeSet.source_preset_id || state.requestedPresetId || null;
    launchTask = defaultTaskForSet();
    browserTask = catalogTasks().includes(browserTask) ? browserTask : launchTask;
    transientMessage = null;
  }

  function serializeItems(items) {
    return items.map((item) => {
      const payload = { task: item.task, item_id: item.item_id };
      if (item.segment_id) {
        payload.segment_id = item.segment_id;
      }
      if (item.note) {
        payload.note = item.note;
      }
      return payload;
    });
  }

  function availableTasks() {
    if (!activeSet) {
      return [];
    }
    return ["wordlist", "text"].filter((taskKey) => (activeSet.taskCounts[taskKey] || 0) > 0);
  }

  function catalogTasks() {
    return ["wordlist", "text"].filter((taskKey) => Array.isArray(state.catalogsByTask[taskKey]));
  }

  function defaultTaskForSet() {
    const tasks = availableTasks();
    if (!tasks.length) {
      return launchTask || "wordlist";
    }
    if (tasks.includes(launchTask)) {
      return launchTask;
    }
    if (activeSet && activeSet.preferred_task && tasks.includes(activeSet.preferred_task)) {
      return activeSet.preferred_task;
    }
    return tasks[0];
  }

  function currentSessionsForTask(taskKey) {
    return state.sessionsByTask[taskKey] || [];
  }

  function firstItemForTask(taskKey) {
    if (!activeSet) {
      return null;
    }
    return activeSet.enrichedItems.find((item) => item.task === taskKey) || null;
  }

  function buildPlayerHref(taskKey, sessionId, focusItemId = null) {
    if (!activeSet || !taskKey || !sessionId) {
      return null;
    }
    const baseHref = state.playerHrefTemplate
      .replace("__SESSION__", encodeURIComponent(sessionId))
      .replace("__TASK__", encodeURIComponent(taskKey));
    const focusItem = focusItemId || (firstItemForTask(taskKey) && firstItemForTask(taskKey).item_id) || null;
    return buildQueryUrl(baseHref, {
      source: "phenomena",
      set_id: activeSet.set_id,
      preset_id: activeSet.source_preset_id || null,
      focus_item: focusItem,
    });
  }

  function syncUrl() {
    const nextUrl = buildQueryUrl(state.phenomenaPageHref, {
      preset_id: (activeSet && activeSet.source_preset_id) || state.requestedPresetId || null,
      set_id: (activeSet && activeSet.set_id) || null,
      task: launchTask || null,
    });
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

  function currentSetStateLabel() {
    if (!activeSet) {
      return "";
    }
    return activeSet.state === "saved"
      ? (labels.stateSaved || "Saved")
      : (labels.stateDraft || "Draft");
  }

  function currentSetDisplayName() {
    if (!activeSet) {
      return "";
    }
    return activeSet.label || activeSet.source_preset_id || activeSet.set_id;
  }

  function renderStatusMeta() {
    if (!statusMeta) {
      return;
    }
    if (!activeSet) {
      statusMeta.hidden = true;
      statusMeta.textContent = "";
      return;
    }
    statusMeta.hidden = false;
    statusMeta.textContent = [currentSetStateLabel(), currentSetDisplayName()].filter(Boolean).join(" · ");
  }

  function setStatus(title, text, actions = []) {
    if (statusHeading) {
      statusHeading.textContent = title;
    }
    if (statusText) {
      statusText.textContent = text;
    }
    if (!statusActions) {
      return;
    }
    statusActions.innerHTML = "";
    for (const action of actions) {
      const element = document.createElement(action.href ? "a" : "button");
      element.className = action.className || "pm-research-button pm-research-button--subtle";
      element.textContent = action.label;
      if (action.href) {
        element.href = action.href;
      } else {
        element.type = "button";
        element.dataset.phenomenaAction = action.action;
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
      saveHint.textContent = labels.saveHint || "Save the current draft as a new set.";
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
      setDialogError(labels.saveValidationError || "Please enter a name.");
      return;
    }

    setSavePending(true);
    setDialogError("");
    try {
      const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(activeSet.set_id)}/save-as`, {
        method: "POST",
        body: { label },
      });
      applySet(payload.set);
      closeSaveDialog();
      setFeedback(`${labels.saveSuccessPrefix || "Saved as"} ${label}`, "success");
      render();
    } catch (error) {
      setSavePending(false);
      if (error.status === 401) {
        closeSaveDialog();
        redirectToLogin({ setId: activeSet.set_id, task: launchTask });
        return;
      }
      if (error.status === 400) {
        setDialogError((error.payload && error.payload.error) || labels.saveValidationError || "Please enter a name.");
        return;
      }
      setDialogError((error.payload && error.payload.error) || labels.saveBackendError || labels.saveErrorFallback || "Action failed.");
    }
  }

  function renderPresetStates() {
    const activePresetId = (activeSet && activeSet.source_preset_id) || state.requestedPresetId || null;
    for (const card of presetCards) {
      card.classList.toggle("is-active", card.dataset.phenomenaPresetCard === activePresetId);
    }
  }

  function renderLauncher() {
    if (!launcherPanel || !launchTaskSelect || !launchSessionSelect || !comparisonLink || !playerLink || !playerNote) {
      return;
    }
    if (!activeSet) {
      launcherPanel.hidden = true;
      return;
    }

    launcherPanel.hidden = false;
    const tasks = availableTasks();
    launchTask = tasks.includes(launchTask) ? launchTask : defaultTaskForSet();

    Array.from(launchTaskSelect.options).forEach((option) => {
      option.disabled = !tasks.includes(option.value);
      option.selected = option.value === launchTask;
    });

    const sessions = currentSessionsForTask(launchTask);
    const currentValue = launchSessionSelect.value;
    launchSessionSelect.innerHTML = sessions
      .map((entry) => `<option value="${escapeHtml(entry.session_id)}">${escapeHtml(entry.label)}</option>`)
      .join("");

    const nextSessionId = sessions.some((entry) => entry.session_id === currentValue)
      ? currentValue
      : (sessions[0] && sessions[0].session_id) || "";
    if (nextSessionId) {
      launchSessionSelect.value = nextSessionId;
    }

    comparisonLink.href = buildQueryUrl(state.comparisonBaseHref, {
      set_id: activeSet.set_id,
      task: launchTask,
    });

    const href = buildPlayerHref(launchTask, nextSessionId);
    if (href) {
      playerLink.href = href;
      playerLink.setAttribute("aria-disabled", "false");
      playerLink.classList.remove("is-disabled");
      playerNote.hidden = true;
      playerNote.textContent = "";
    } else {
      playerLink.href = "#";
      playerLink.setAttribute("aria-disabled", "true");
      playerLink.classList.add("is-disabled");
      playerNote.hidden = false;
      playerNote.textContent = labels.playerUnavailable || "No session available.";
    }
  }

  function renderItems() {
    if (!itemsPanel || !itemsList || !itemsSummary) {
      return;
    }
    if (!activeSet) {
      itemsPanel.hidden = true;
      return;
    }

    itemsPanel.hidden = false;
    const sourceLine = activeSet.source_preset_id
      ? `${labels.workspaceSource || "Preset"}: ${activeSet.source_preset_id}`
      : `${labels.workspaceSetId || "Set ID"}: ${activeSet.set_id}`;
    itemsSummary.textContent = `${activeSet.enrichedItems.length} ${labels.workspaceItems || "items"} · ${sourceLine}`;
    itemsList.innerHTML = activeSet.enrichedItems
      .map((item) => {
        const groupLine = item.groupId ? `<span class="pm-phenomena-item__meta">${escapeHtml(item.groupId)}</span>` : "";
        const removeButton = state.isAuthenticated
          ? `<button type="button" class="pm-research-inline-action pm-research-inline-action--compact pm-research-inline-action--secondary" data-phenomena-remove-item="${escapeHtml(item.task)}:${escapeHtml(item.item_id)}">${escapeHtml(labels.removeLabel || "Remove")}</button>`
          : "";
        return `
          <li class="pm-phenomena-item">
            <div class="pm-phenomena-item__body">
              <div class="pm-phenomena-item__meta-row">
                <span class="pm-phenomena-item__number">${escapeHtml(item.itemNumber)}</span>
                <span class="pm-phenomena-item__task">${escapeHtml(item.taskLabel)}</span>
                ${groupLine}
              </div>
              <p class="pm-phenomena-item__text">${escapeHtml(item.text)}</p>
            </div>
            <div class="pm-phenomena-item__actions">
              ${removeButton}
            </div>
          </li>
        `;
      })
      .join("");
  }

  function renderBrowser() {
    if (!browserPanel || !browserResults || !browserSummary || !browserTaskSelect || !searchInput) {
      return;
    }
    if (!activeSet) {
      browserPanel.hidden = true;
      return;
    }

    browserPanel.hidden = false;
    const tasks = catalogTasks();
    browserTask = tasks.includes(browserTask) ? browserTask : tasks[0] || "wordlist";
    Array.from(browserTaskSelect.options).forEach((option) => {
      option.disabled = !tasks.includes(option.value);
      option.selected = option.value === browserTask;
    });

    const selectedKeys = new Set(activeSet.enrichedItems.map((item) => `${item.task}:${item.item_id}`));
    const allEntries = state.catalogsByTask[browserTask] || [];
    const normalizedSearch = searchTerm.trim().toLowerCase();
    const matchingEntries = allEntries.filter((item) => {
      if (selectedKeys.has(`${item.task}:${item.item_id}`)) {
        return false;
      }
      if (!normalizedSearch) {
        return true;
      }
      const haystack = `${item.item_number} ${item.text} ${item.group_id || ""}`.toLowerCase();
      return haystack.includes(normalizedSearch);
    });
    const visibleEntries = matchingEntries.slice(0, 24);

    browserSummary.textContent = `${matchingEntries.length} ${labels.catalogCountLabel || "available catalog entries"}`;
    if (!visibleEntries.length) {
      browserResults.innerHTML = `<li class="pm-phenomena-browser-results__empty">${escapeHtml(labels.browserEmpty || "No matching entries.")}</li>`;
      return;
    }

    browserResults.innerHTML = visibleEntries
      .map((item) => `
        <li class="pm-phenomena-browser-result">
          <div class="pm-phenomena-browser-result__body">
            <div class="pm-phenomena-browser-result__meta">
              <span class="pm-phenomena-browser-result__number">${escapeHtml(item.item_number)}</span>
              <span class="pm-phenomena-browser-result__task">${escapeHtml(item.task_label)}</span>
              ${item.group_id ? `<span class="pm-phenomena-browser-result__group">${escapeHtml(item.group_id)}</span>` : ""}
            </div>
            <p class="pm-phenomena-browser-result__text">${escapeHtml(item.text)}</p>
          </div>
          <button type="button" class="pm-research-inline-action pm-research-inline-action--compact pm-research-inline-action--secondary" data-phenomena-add-item="${escapeHtml(item.task)}:${escapeHtml(item.item_id)}">${escapeHtml(labels.addLabel || "Add")}</button>
        </li>
      `)
      .join("");
  }

  function renderStatus() {
    if (transientMessage) {
      setStatus(labels.statusTitle || "Workspace", transientMessage, []);
      return;
    }
    if (activeSet) {
      const summary = `${activeSet.enrichedItems.length} ${labels.workspaceItems || "items"} · ${(labels.workspaceSource || "Preset")}: ${activeSet.source_preset_id || "manual"}`;
      setStatus(labels.workspaceReady || "Ready", summary, state.isAuthenticated
        ? [{ label: labels.saveAsLabel || labels.saveLabel || "Save as new set", action: "save" }]
        : []);
      return;
    }
    if (!state.isAuthenticated && (state.requestedPresetId || state.requestedSetId)) {
      setStatus(labels.emptyTitle || "No draft loaded", labels.loginText || "Please sign in.", [
        {
          label: labels.loginLabel || "Login",
          href: buildQueryUrl(state.loginHref, { next: buildQueryUrl(state.phenomenaPageHref, { preset_id: state.requestedPresetId || null, set_id: state.requestedSetId || null, task: launchTask || null }) }),
        },
      ]);
      return;
    }
    if (state.requestedSetId) {
      setStatus(labels.statusTitle || "Workspace", labels.loadingSet || "Loading set...", []);
      return;
    }
    if (state.requestedPresetId) {
      setStatus(labels.statusTitle || "Workspace", labels.openingPreset || "Opening preset...", []);
      return;
    }
    setStatus(labels.emptyTitle || "No draft loaded", labels.emptyText || "Open a preset.", !state.isAuthenticated ? [{ label: labels.loginLabel || "Login", href: state.loginHref }] : []);
  }

  function render() {
    renderStatus();
    renderStatusMeta();
    setFeedback(feedbackState && feedbackState.message, feedbackState && feedbackState.tone);
    renderPresetStates();
    renderLauncher();
    renderItems();
    renderBrowser();
    syncUrl();
  }

  async function loadSet(setId) {
    transientMessage = labels.loadingSet || "Loading set...";
    render();
    try {
      const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(setId)}`);
      applySet(payload.set);
      render();
    } catch (error) {
      transientMessage = null;
      if (error.status === 401) {
        redirectToLogin({ setId });
        return;
      }
      setStatus(labels.emptyTitle || "No draft loaded", error.message || labels.saveErrorFallback || "Action failed.", !state.isAuthenticated ? [{ label: labels.loginLabel || "Login", href: state.loginHref }] : []);
    }
  }

  async function createPresetDraft(presetId, preferredTask) {
    transientMessage = labels.openingPreset || "Opening preset...";
    render();
    try {
      const payload = await requestJson(state.createSetHref, {
        method: "POST",
        body: {
          corpus_language: state.languageSlug,
          preset_id: presetId,
          preferred_task: preferredTask || undefined,
        },
      });
      applySet(payload.set);
      launchTask = activeSet.preferred_task || preferredTask || defaultTaskForSet();
      browserTask = launchTask;
      render();
    } catch (error) {
      transientMessage = null;
      if (error.status === 401) {
        redirectToLogin({ presetId, task: preferredTask });
        return;
      }
      setStatus(labels.emptyTitle || "No draft loaded", error.message || labels.saveErrorFallback || "Action failed.", !state.isAuthenticated ? [{ label: labels.loginLabel || "Login", href: state.loginHref }] : []);
    }
  }

  async function replaceItems(nextItems) {
    if (!activeSet) {
      return;
    }
    transientMessage = labels.statusTitle || "Updating...";
    render();
    try {
      const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(activeSet.set_id)}/items`, {
        method: "PUT",
        body: { items: nextItems },
      });
      applySet(payload.set);
      launchTask = defaultTaskForSet();
      browserTask = catalogTasks().includes(browserTask) ? browserTask : launchTask;
      render();
    } catch (error) {
      transientMessage = null;
      if (error.status === 401) {
        redirectToLogin({ setId: activeSet.set_id });
        return;
      }
      setStatus(labels.statusTitle || "Workspace", error.message || labels.saveErrorFallback || "Action failed.", []);
    }
  }

  async function persistPreferredTask(taskKey) {
    if (!activeSet) {
      return;
    }
    try {
      const payload = await requestJson(`${state.setApiBaseHref}/${encodeURIComponent(activeSet.set_id)}`, {
        method: "PATCH",
        body: { preferred_task: taskKey },
      });
      applySet(payload.set);
      render();
    } catch {
      render();
    }
  }

  root.addEventListener("click", (event) => {
    const saveAction = event.target.closest("[data-phenomena-action='save']");
    if (!saveAction) {
      return;
    }
    event.preventDefault();
    if (!state.isAuthenticated || !activeSet) {
      setFeedback(labels.saveUnavailable || labels.loginText || "Please sign in.", "error");
      if (!state.isAuthenticated) {
        redirectToLogin({ setId: activeSet && activeSet.set_id, task: launchTask });
      }
      return;
    }
    openSaveDialog();
  });

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

  presetButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const presetId = button.dataset.phenomenaOpenPreset;
      const preferredTask = button.dataset.phenomenaPreferredTask || "wordlist";
      if (!state.isAuthenticated) {
        redirectToLogin({ presetId, task: preferredTask });
        return;
      }
      createPresetDraft(presetId, preferredTask);
    });
  });

  if (browserTaskSelect) {
    browserTaskSelect.addEventListener("change", () => {
      browserTask = browserTaskSelect.value;
      renderBrowser();
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      searchTerm = searchInput.value || "";
      renderBrowser();
    });
  }

  if (launchTaskSelect) {
    launchTaskSelect.addEventListener("change", () => {
      launchTask = launchTaskSelect.value;
      renderLauncher();
      syncUrl();
      persistPreferredTask(launchTask);
    });
  }

  if (launchSessionSelect) {
    launchSessionSelect.addEventListener("change", () => {
      renderLauncher();
      syncUrl();
    });
  }

  if (browserResults) {
    browserResults.addEventListener("click", (event) => {
      const button = event.target.closest("[data-phenomena-add-item]");
      if (!button || !activeSet) {
        return;
      }
      const [task, itemId] = String(button.dataset.phenomenaAddItem || "").split(":");
      if (!task || !itemId) {
        return;
      }
      const nextItems = serializeItems(activeSet.enrichedItems);
      nextItems.push({ task, item_id: itemId });
      replaceItems(nextItems);
    });
  }

  if (itemsList) {
    itemsList.addEventListener("click", (event) => {
      const button = event.target.closest("[data-phenomena-remove-item]");
      if (!button || !activeSet) {
        return;
      }
      const [task, itemId] = String(button.dataset.phenomenaRemoveItem || "").split(":");
      if (!task || !itemId) {
        return;
      }
      const nextItems = serializeItems(
        activeSet.enrichedItems.filter((item) => !(item.task === task && item.item_id === itemId)),
      );
      replaceItems(nextItems);
    });
  }

  render();

  if (state.isAuthenticated && state.requestedSetId) {
    loadSet(state.requestedSetId);
    return;
  }

  if (state.isAuthenticated && state.requestedPresetId) {
    const preset = presetLookup.get(state.requestedPresetId);
    if (preset) {
      createPresetDraft(preset.presetId, preset.preferredTask || "wordlist");
    }
  }
}

init();