import { getCsrfToken } from "../api.js";
import { fetchWithAuth } from "../modules/auth/fetch.js";
import { showSnackbar } from "../modules/core/snackbar.js";

let requestFailedLabel = "";

function parseState() {
  const element = document.getElementById("pm-phenomena-editor-state");
  if (!element) {
    return null;
  }

  try {
    return JSON.parse(element.textContent || "{}");
  } catch {
    return null;
  }
}

function buildUrl(template, value) {
  return template.replace("__SET_ID__", encodeURIComponent(value));
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

  if (["POST", "PATCH", "PUT", "DELETE"].includes(method)) {
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
    throw error;
  }
  return payload;
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function itemKey(task, itemId) {
  return `${task}:${itemId}`;
}

function init() {
  const state = parseState();
  const root = document.querySelector("[data-phenomena-editor-root]");
  if (!state || !root) {
    return;
  }
  requestFailedLabel = state.labels?.requestFailed || requestFailedLabel;

  const titleInput = root.querySelector("[data-phenomena-title-input]");
  const noteInput = root.querySelector("[data-phenomena-note-input]");
  const saveButton = root.querySelector("[data-phenomena-save-action]");
  const saveButtonLabel = root.querySelector("[data-phenomena-save-label]");
  const discardButton = root.querySelector("[data-phenomena-discard-action]");
  const curatedToggleButton = root.querySelector("[data-phenomena-curated-toggle-action]");
  const curatedToggleLabel = root.querySelector("[data-phenomena-curated-toggle-label]");
  const typeBadge = root.querySelector("[data-phenomena-type-badge]");
  const stateBadge = root.querySelector("[data-phenomena-state-badge]");
  const statusText = root.querySelector("[data-phenomena-status-text]");
  const curatedHint = root.querySelector("[data-phenomena-curated-hint]");
  const selectedList = root.querySelector("[data-phenomena-selected-list]");
  const selectedEmpty = root.querySelector("[data-phenomena-selected-empty]");
  const pageTitle = document.getElementById("promat-page-title");
  const breadcrumbCurrent = document.querySelector(".pm-breadcrumb__item.is-current .pm-breadcrumb__link--current");
  const confirmDialog = document.querySelector("[data-phenomena-editor-confirm]");
  const confirmTitle = document.querySelector("[data-phenomena-editor-confirm-title]");
  const confirmMessage = document.querySelector("[data-phenomena-editor-confirm-message]");
  const confirmCancel = document.querySelector("[data-phenomena-editor-confirm-cancel]");
  const confirmSubmit = document.querySelector("[data-phenomena-editor-confirm-submit]");
  const confirmSubmitLabel = document.querySelector("[data-phenomena-editor-confirm-submit-label]");

  const searchInputs = {
    wordlist: root.querySelector('[data-phenomena-source-search="wordlist"]'),
    text: root.querySelector('[data-phenomena-source-search="text"]'),
  };
  const sourceLists = {
    wordlist: root.querySelector('[data-phenomena-source-list="wordlist"]'),
    text: root.querySelector('[data-phenomena-source-list="text"]'),
  };

  let record = clone(state.initialRecord);
  let selectedItems = (record.items || []).slice().sort((left, right) => (left.sort_order || 0) - (right.sort_order || 0));
  let baseline = snapshot();
  let saveCompleted = false;
  let draggedIndex = null;
  let dropTargetIndex = null;
  let dropPlacement = "before";
  let dragImage = null;
  let pending = false;
  let confirmAction = null;
  let suppressBeforeUnload = false;

  function showDialog(dialog) {
    if (dialog && typeof dialog.showModal === "function" && !dialog.open) {
      dialog.showModal();
    }
  }

  function closeDialog(dialog) {
    if (dialog && typeof dialog.close === "function" && dialog.open) {
      dialog.close();
    }
  }

  function resetConfirmDialog() {
    confirmAction = null;
    confirmDialog?.classList.remove("pm-dialog--danger");
    confirmSubmit?.classList.remove("pm-action-button--danger");
    confirmSubmit?.classList.add("pm-action-button--primary");
    if (confirmTitle) {
      confirmTitle.textContent = "";
    }
    if (confirmMessage) {
      confirmMessage.textContent = "";
    }
    if (confirmSubmitLabel) {
      confirmSubmitLabel.textContent = "";
    }
  }

  function closePhenomenaDialogs() {
    closeDialog(confirmDialog);
  }

  function catalogs(taskKey) {
    return state.catalogsByTask[taskKey] || [];
  }

  function findCatalogItem(taskKey, itemId) {
    return catalogs(taskKey).find((item) => item.item_id === itemId) || null;
  }

  function snapshot() {
    return JSON.stringify({
      label: (titleInput?.value || "").trim(),
      note: (noteInput?.value || "").trim(),
      items: selectedItems.map((item, index) => ({
        task: item.task,
        item_id: item.item_id,
        segment_id: item.segment_id || null,
        note: item.note || null,
        sort_order: index + 1,
      })),
    });
  }

  function isDirty() {
    return snapshot() !== baseline;
  }

  function isCuratedRecord() {
    return record?.visibility === "curated";
  }

  function isCuratedAdminRecord() {
    return state.isAdmin && isCuratedRecord();
  }

  function currentTypeKey() {
    return state.editorMode === "preset" ? "curated" : "custom";
  }

  function currentStateKey() {
    if (isDirty()) {
      return "unsaved";
    }
    if (isCuratedRecord() && record.lifecycle === "archived") {
      return "archived";
    }
    if (saveCompleted || record.state === "saved") {
      return "saved";
    }
    if (state.editorMode === "preset") {
      return null;
    }
    if (selectedItems.length === 0 && !(noteInput?.value || "").trim()) {
      return "new";
    }
    return "unsaved";
  }

  function visibleTitle() {
    const fallback = state.labels.untitled || "";
    return (titleInput?.value || "").trim() || record.label || fallback;
  }

  function syncHeadingTitle() {
    const title = visibleTitle();
    if (pageTitle) {
      pageTitle.textContent = title;
    }
    if (breadcrumbCurrent) {
      breadcrumbCurrent.textContent = title;
    }
  }

  function syncSaveAction() {
    if (!saveButton) {
      return;
    }
    const allowWithoutDirty = state.editorMode === "set" && record.state !== "saved";
    const disabled = pending || (!isDirty() && !allowWithoutDirty);
    saveButton.disabled = disabled;
    saveButton.classList.toggle("is-disabled", disabled);
    if (saveButtonLabel) {
      saveButtonLabel.textContent = isCuratedAdminRecord() ? state.labels.updateCurated : state.labels.save;
    }
  }

  async function performSave() {
    if (pending) {
      return;
    }
    if (!state.isAuthenticated) {
      window.location.href = state.loginHref;
      return;
    }
    pending = true;
    syncStatus();
    try {
      await persistCurrentRecord();
      showSnackbar(state.labels.saveSuccess, "success");
      closeDialog(confirmDialog);
    } catch (error) {
      showSnackbar(error.message || state.labels.saveError, "error");
    } finally {
      pending = false;
      syncStatus();
    }
  }

  function syncStatus() {
    const typeKey = currentTypeKey();
    const stateKey = currentStateKey();
    if (typeBadge) {
      typeBadge.textContent = state.statusLabels[typeKey] || typeKey;
      typeBadge.className = `pm-comparison-speaker-badge pm-phenomena-badge pm-phenomena-badge--${typeKey}`;
    }
    if (stateBadge) {
      stateBadge.hidden = !stateKey;
      if (stateKey) {
        stateBadge.textContent = state.statusLabels[stateKey] || stateKey;
        stateBadge.className = `pm-comparison-speaker-badge pm-phenomena-badge pm-phenomena-badge--${stateKey}`;
      }
    }
    if (statusText) {
      if (stateKey === "unsaved") {
        statusText.textContent = state.labels.unsavedStateText;
      } else if (stateKey === "archived") {
        statusText.textContent = state.labels.archivedStateText;
      } else if (stateKey === "saved") {
        statusText.textContent = state.labels.savedStateText;
      } else {
        statusText.textContent = "";
      }
    }
    if (curatedHint) {
      if (isCuratedAdminRecord()) {
        curatedHint.textContent = state.labels.curatedAdminHint;
        curatedHint.hidden = false;
      } else {
        curatedHint.textContent = state.labels.curatedHint;
        curatedHint.hidden = !(isCuratedRecord() || (record.source_preset_id && (state.editorMode === "preset" || record.state === "draft")));
      }
    }
    if (discardButton) {
      discardButton.textContent = isCuratedRecord() ? state.labels.discard : (record.state === "saved" ? state.labels.delete : state.labels.discard);
    }
    if (curatedToggleButton) {
      const showCuratedToggle = isCuratedAdminRecord();
      curatedToggleButton.hidden = !showCuratedToggle;
      curatedToggleButton.disabled = pending;
      curatedToggleButton.classList.toggle("is-disabled", pending);
      if (curatedToggleLabel) {
        curatedToggleLabel.textContent = record.lifecycle === "archived" ? state.labels.reactivateCurated : state.labels.archiveCurated;
      }
    }
    syncHeadingTitle();
    syncSaveAction();
  }

  function currentSelectionMap() {
    return new Map(selectedItems.map((item, index) => [itemKey(item.task, item.item_id), { item, index }]));
  }

  function normalizeSelectedItems() {
    selectedItems = selectedItems.map((item, index) => ({
      ...item,
      sort_order: index + 1,
    }));
  }

  function renderSourceList(taskKey) {
    const list = sourceLists[taskKey];
    if (!list) {
      return;
    }
    list.innerHTML = "";
    const term = (searchInputs[taskKey]?.value || "").trim().toLowerCase();
    const selectionMap = currentSelectionMap();

    catalogs(taskKey)
      .filter((item) => {
        if (!term) {
          return true;
        }
        return `${item.item_number || ""} ${item.text || ""}`.toLowerCase().includes(term);
      })
      .forEach((item) => {
        const key = itemKey(taskKey, item.item_id);
        const selected = selectionMap.has(key);
        const li = document.createElement("li");
        li.className = `pm-phenomena-source-item${selected ? " is-selected" : ""}`;

        const button = document.createElement("button");
        button.type = "button";
        button.className = "pm-phenomena-source-item__button";
        button.dataset.toggleSelection = key;
        button.dataset.task = taskKey;
        button.dataset.itemId = item.item_id;
        button.setAttribute("aria-pressed", selected ? "true" : "false");

        const meta = document.createElement("span");
        meta.className = "pm-player-list__number pm-phenomena-source-item__meta";
        meta.textContent = item.item_number || item.item_id;

        const body = document.createElement("span");
        body.className = "pm-phenomena-source-item__body";

        const text = document.createElement("span");
        text.className = "pm-player-list__text pm-phenomena-source-item__text";
        text.textContent = item.text || item.item_id;

        const marker = document.createElement("span");
        marker.className = "pm-phenomena-source-item__marker";
        marker.textContent = selected ? "✓" : "+";

        body.append(text);
        button.append(meta, body, marker);
        li.append(button);
        list.append(li);
      });
  }

  function renderSelectedList() {
    if (!selectedList) {
      return;
    }
    normalizeSelectedItems();
    selectedList.innerHTML = "";
    selectedEmpty.hidden = selectedItems.length > 0;

    selectedItems.forEach((item, index) => {
      const catalogItem = findCatalogItem(item.task, item.item_id);
      const li = document.createElement("li");
      li.className = "pm-phenomena-selected-item";
      li.draggable = true;
      li.dataset.index = String(index);
      li.classList.toggle("is-drop-target", dropTargetIndex === index);

      const position = document.createElement("span");
      position.className = "pm-player-list__number pm-phenomena-selected-item__position";
      position.textContent = String(index + 1);

      const body = document.createElement("div");
      body.className = "pm-phenomena-selected-item__body";

      const meta = document.createElement("div");
      meta.className = "pm-phenomena-selected-item__meta";
      meta.textContent = `${state.labels[item.task === "text" ? "typeText" : "typeWordlist"]} · ${catalogItem?.item_number || item.item_id}`;

      const text = document.createElement("div");
      text.className = "pm-player-list__text pm-phenomena-selected-item__text";
      text.textContent = catalogItem?.text || item.item_id;

      body.append(meta, text);

      const actions = document.createElement("div");
      actions.className = "pm-phenomena-selected-item__actions";

      const handle = document.createElement("button");
      handle.type = "button";
      handle.className = "pm-phenomena-selected-item__handle";
      handle.textContent = "⋮⋮";
      handle.setAttribute("aria-label", state.labels.dragHandle);
      handle.setAttribute("title", state.labels.dragHandle);
      handle.tabIndex = -1;

      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "pm-phenomena-selected-item__remove";
      remove.dataset.removeSelection = itemKey(item.task, item.item_id);
      remove.textContent = "×";
      remove.setAttribute("aria-label", state.labels.remove);
      remove.setAttribute("title", state.labels.remove);

      actions.append(handle, remove);
      li.append(position, body, actions);
      selectedList.append(li);
    });
  }

  function renderAll() {
    renderSourceList("wordlist");
    renderSourceList("text");
    renderSelectedList();
    syncStatus();
  }

  function clearDragImage() {
    if (dragImage && dragImage.isConnected) {
      dragImage.remove();
    }
    dragImage = null;
  }

  function clearDropTarget() {
    selectedList?.querySelectorAll(".pm-phenomena-selected-item.is-drop-target").forEach((item) => {
      item.classList.remove("is-drop-target");
      delete item.dataset.dropPosition;
    });
  }

  function setDropTarget(item, placement) {
    clearDropTarget();
    if (!item) {
      dropTargetIndex = null;
      return;
    }
    item.classList.add("is-drop-target");
    item.dataset.dropPosition = placement;
    dropTargetIndex = Number(item.dataset.index);
    dropPlacement = placement;
  }

  function resetDragState() {
    draggedIndex = null;
    dropTargetIndex = null;
    dropPlacement = "before";
    selectedList?.querySelectorAll(".pm-phenomena-selected-item.is-dragging").forEach((item) => {
      item.classList.remove("is-dragging");
    });
    clearDropTarget();
    clearDragImage();
  }

  function buildDragImage(item) {
    const clone = item.cloneNode(true);
    clone.classList.add("is-drag-ghost");
    clone.style.position = "fixed";
    clone.style.top = "-9999px";
    clone.style.left = "-9999px";
    clone.style.width = `${item.getBoundingClientRect().width}px`;
    clone.style.pointerEvents = "none";
    document.body.append(clone);
    return clone;
  }

  function selectedIndex(key) {
    return selectedItems.findIndex((item) => itemKey(item.task, item.item_id) === key);
  }

  function toggleSelection(taskKey, itemId) {
    saveCompleted = false;
    const key = itemKey(taskKey, itemId);
    const index = selectedIndex(key);
    if (index >= 0) {
      selectedItems.splice(index, 1);
    } else {
      selectedItems.push({ task: taskKey, item_id: itemId });
    }
    renderAll();
  }

  function applySelectionBulk(taskKey, mode) {
    saveCompleted = false;
    const term = (searchInputs[taskKey]?.value || "").trim().toLowerCase();
    const visibleItems = catalogs(taskKey).filter((item) => {
      if (!term) {
        return true;
      }
      return `${item.item_number || ""} ${item.text || ""}`.toLowerCase().includes(term);
    });

    if (mode === "add") {
      visibleItems.forEach((item) => {
        if (selectedIndex(itemKey(taskKey, item.item_id)) < 0) {
          selectedItems.push({ task: taskKey, item_id: item.item_id });
        }
      });
    } else {
      const visibleKeys = new Set(visibleItems.map((item) => itemKey(taskKey, item.item_id)));
      selectedItems = selectedItems.filter((item) => !visibleKeys.has(itemKey(item.task, item.item_id)));
    }
    renderAll();
  }

  async function persistCurrentRecord() {
    const label = (titleInput?.value || "").trim();
    const note = (noteInput?.value || "").trim();
    const itemsPayload = selectedItems.map((item, index) => ({
      task: item.task,
      item_id: item.item_id,
      sort_order: index + 1,
      ...(item.segment_id ? { segment_id: item.segment_id } : {}),
      ...(item.note ? { note: item.note } : {}),
    }));

    let setId = record.set_id;
    if (isCuratedAdminRecord()) {
      const updated = await requestJson(buildUrl(state.adminUpdateCuratedSetUrlTemplate, record.set_id), {
        method: "PUT",
        body: {
          label,
          note,
          items: itemsPayload,
        },
      });
      record = updated.set;
      selectedItems = (record.items || []).slice().sort((left, right) => (left.sort_order || 0) - (right.sort_order || 0));
      baseline = snapshot();
      saveCompleted = true;
      renderAll();
      return;
    }
    if (state.editorMode === "preset") {
      const created = await requestJson(state.createSetUrl, {
        method: "POST",
        body: {
          corpus_language: state.languageSlug,
          preset_id: record.source_preset_id,
          label,
          note,
        },
      });
      setId = created?.set?.set_id;
      if (!setId) {
        throw new Error(state.labels.saveError);
      }
      state.editorMode = "set";
    }

    await requestJson(buildUrl(state.putItemsUrlTemplate, setId), {
      method: "PUT",
      body: { items: itemsPayload },
    });

    const patched = await requestJson(buildUrl(state.patchSetUrlTemplate, setId), {
      method: "PATCH",
      body: {
        label,
        note,
        state: "saved",
      },
    });
    record = patched.set;
    selectedItems = (record.items || []).slice().sort((left, right) => (left.sort_order || 0) - (right.sort_order || 0));
    baseline = snapshot();
    saveCompleted = true;
    if (record.set_id) {
      window.history.replaceState({}, "", buildUrl(state.setEditorHrefTemplate, record.set_id));
    }
    renderAll();
  }

  function openConfirm(title, message, confirmLabel, action, variant = "standard") {
    confirmAction = action;
    confirmDialog?.classList.toggle("pm-dialog--danger", variant === "danger");
    if (confirmTitle) {
      confirmTitle.textContent = title;
    }
    if (confirmMessage) {
      confirmMessage.textContent = message;
    }
    if (confirmSubmit) {
      confirmSubmit.classList.toggle("pm-action-button--danger", variant === "danger");
      confirmSubmit.classList.toggle("pm-action-button--primary", variant !== "danger");
    }
    if (confirmSubmitLabel) {
      confirmSubmitLabel.textContent = confirmLabel;
    }
    showDialog(confirmDialog);
  }

  function navigateToOverview() {
    suppressBeforeUnload = true;
    window.location.href = state.overviewHref;
  }

  function navigateToHref(href) {
    if (!href) {
      return;
    }
    suppressBeforeUnload = true;
    window.location.href = href;
  }

  async function discardOrDelete() {
    const dirty = isDirty();
    if (isCuratedRecord()) {
      if (!dirty) {
        navigateToOverview();
        return;
      }
      openConfirm(state.labels.discardTitle, state.labels.discardMessage, state.labels.confirmDiscard, () => {
        navigateToOverview();
      }, "standard");
      return;
    }
    if (!record.set_id) {
      if (!dirty) {
        navigateToOverview();
        return;
      }
      openConfirm(state.labels.discardTitle, state.labels.discardMessage, state.labels.confirmDiscard, () => {
        navigateToOverview();
      }, "standard");
      return;
    }

    const isSavedCustom = record.state === "saved";
    const title = isSavedCustom ? state.labels.deleteTitle : state.labels.discardTitle;
    const message = isSavedCustom
      ? state.labels.deleteMessage.replace("{label}", (titleInput?.value || record.label || "").trim())
      : state.labels.discardMessage;
    const confirmLabel = isSavedCustom ? state.labels.confirmDelete : state.labels.confirmDiscard;
    openConfirm(title, message, confirmLabel, async () => {
      await requestJson(buildUrl(state.deleteSetUrlTemplate, record.set_id), { method: "DELETE" });
      navigateToOverview();
    }, isSavedCustom ? "danger" : "standard");
  }

  async function toggleCuratedLifecycle() {
    const archived = record.lifecycle === "archived";
    const title = archived ? state.labels.reactivateCuratedTitle : state.labels.archiveCuratedTitle;
    const message = archived ? state.labels.reactivateCuratedMessage : state.labels.archiveCuratedMessage;
    const confirmLabel = archived ? state.labels.reactivateCurated : state.labels.archiveCurated;
    openConfirm(title, message, confirmLabel, async () => {
      const response = await requestJson(
        buildUrl(archived ? state.adminReactivateCuratedSetUrlTemplate : state.adminArchiveCuratedSetUrlTemplate, record.set_id),
        { method: "POST" },
      );
      record = response.set;
      selectedItems = (record.items || []).slice().sort((left, right) => (left.sort_order || 0) - (right.sort_order || 0));
      baseline = snapshot();
      saveCompleted = true;
      renderAll();
      showSnackbar(archived ? state.labels.reactivateSuccess : state.labels.archiveSuccess, "success");
    }, archived ? "standard" : "danger");
  }

  titleInput.value = record.label || "";
  noteInput.value = record.note || "";
  baseline = snapshot();
  renderAll();

  titleInput.addEventListener("input", () => {
    saveCompleted = false;
    syncStatus();
  });
  noteInput.addEventListener("input", () => {
    saveCompleted = false;
    syncStatus();
  });

  Object.entries(searchInputs).forEach(([taskKey, input]) => {
    input?.addEventListener("input", () => renderSourceList(taskKey));
  });

  root.addEventListener("click", (event) => {
    const toggleButton = event.target.closest("[data-toggle-selection]");
    if (toggleButton) {
      toggleSelection(toggleButton.dataset.task, toggleButton.dataset.itemId);
      return;
    }

    const removeButton = event.target.closest("[data-remove-selection]");
    if (removeButton) {
      const [taskKey, itemId] = removeButton.dataset.removeSelection.split(":");
      toggleSelection(taskKey, itemId);
      return;
    }

    const selectAllButton = event.target.closest("[data-phenomena-select-all]");
    if (selectAllButton) {
      applySelectionBulk(selectAllButton.dataset.phenomenaSelectAll, "add");
      return;
    }

    const clearAllButton = event.target.closest("[data-phenomena-clear-all]");
    if (clearAllButton) {
      applySelectionBulk(clearAllButton.dataset.phenomenaClearAll, "remove");
    }
  });

  selectedList?.addEventListener("dragstart", (event) => {
    const item = event.target.closest(".pm-phenomena-selected-item");
    if (!item) {
      return;
    }
    draggedIndex = Number(item.dataset.index);
    dropPlacement = "before";
    item.classList.add("is-dragging");
    clearDragImage();
    if (event.dataTransfer) {
      const rect = item.getBoundingClientRect();
      dragImage = buildDragImage(item);
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", String(draggedIndex));
      event.dataTransfer.setDragImage(dragImage, Math.min(64, rect.width / 3), 24);
    }
  });

  selectedList?.addEventListener("dragend", () => {
    resetDragState();
  });

  selectedList?.addEventListener("dragover", (event) => {
    event.preventDefault();
    const item = event.target.closest(".pm-phenomena-selected-item");
    if (item) {
      const targetIndex = Number(item.dataset.index);
      if (!Number.isNaN(targetIndex) && targetIndex !== draggedIndex) {
        const bounds = item.getBoundingClientRect();
        const placement = event.clientY >= bounds.top + bounds.height / 2 ? "after" : "before";
        if (targetIndex !== dropTargetIndex || placement !== dropPlacement) {
          setDropTarget(item, placement);
        }
      } else {
        clearDropTarget();
        dropTargetIndex = null;
      }
    } else if (selectedList?.lastElementChild && draggedIndex !== null) {
      setDropTarget(selectedList.lastElementChild, "after");
    }
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = "move";
    }
  });

  selectedList?.addEventListener("drop", (event) => {
    event.preventDefault();
    let item = event.target.closest(".pm-phenomena-selected-item");
    if (!item && selectedList?.lastElementChild && draggedIndex !== null) {
      item = selectedList.lastElementChild;
      dropPlacement = "after";
    }
    if (!item || draggedIndex === null) {
      resetDragState();
      return;
    }
    const targetIndex = Number(item.dataset.index);
    if (Number.isNaN(targetIndex)) {
      resetDragState();
      return;
    }
    const [moved] = selectedItems.splice(draggedIndex, 1);
    let insertIndex = targetIndex;
    if (dropPlacement === "after") {
      insertIndex += 1;
    }
    if (insertIndex > draggedIndex) {
      insertIndex -= 1;
    }
    insertIndex = Math.max(0, Math.min(insertIndex, selectedItems.length));
    selectedItems.splice(insertIndex, 0, moved);
    saveCompleted = false;
    resetDragState();
    renderAll();
  });

  saveButton?.addEventListener("click", async () => {
    if (pending) {
      return;
    }
    if (isCuratedAdminRecord()) {
      openConfirm(
        state.labels.updateCuratedTitle,
        state.labels.updateCuratedMessage,
        state.labels.updateCurated,
        performSave,
      );
      return;
    }
    await performSave();
  });

  discardButton?.addEventListener("click", async () => {
    if (pending) {
      return;
    }
    try {
      await discardOrDelete();
    } catch (error) {
      showSnackbar(error.message || state.labels.delete, "error");
    }
  });

  curatedToggleButton?.addEventListener("click", async () => {
    if (pending || !isCuratedAdminRecord()) {
      return;
    }
    try {
      await toggleCuratedLifecycle();
    } catch (error) {
      showSnackbar(error.message || state.labels.requestFailed, "error");
    }
  });

  confirmCancel?.addEventListener("click", () => {
    closeDialog(confirmDialog);
  });

  confirmDialog?.addEventListener("close", resetConfirmDialog);

  confirmSubmit?.addEventListener("click", async () => {
    if (!confirmAction || pending) {
      closeDialog(confirmDialog);
      return;
    }
    pending = true;
    try {
      await confirmAction();
      closeDialog(confirmDialog);
    } catch (error) {
      showSnackbar(error.message || state.labels.delete, "error");
    } finally {
      pending = false;
    }
  });

  document.addEventListener("click", (event) => {
    if (event.defaultPrevented || pending || !isDirty()) {
      return;
    }
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }
    const target = event.target;
    if (!(target instanceof Element)) {
      return;
    }
    const link = target.closest("a[href]");
    if (!link) {
      return;
    }
    if (link.closest("[data-phenomena-editor-confirm]")) {
      return;
    }
    if (link.target && link.target !== "_self") {
      return;
    }
    if (link.hasAttribute("download")) {
      return;
    }
    const rawHref = link.getAttribute("href") || "";
    if (!rawHref || rawHref.startsWith("#") || rawHref.startsWith("javascript:") || rawHref.startsWith("mailto:") || rawHref.startsWith("tel:")) {
      return;
    }

    const targetUrl = new URL(link.href, window.location.href);
    const currentUrl = new URL(window.location.href);
    if (targetUrl.origin !== currentUrl.origin || targetUrl.href === currentUrl.href) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    openConfirm(state.labels.discardTitle, state.labels.discardMessage, state.labels.confirmDiscard, () => {
      navigateToHref(targetUrl.toString());
    });
  }, true);

  window.addEventListener("pagehide", closePhenomenaDialogs);

  window.addEventListener("beforeunload", (event) => {
    closePhenomenaDialogs();
    if (suppressBeforeUnload || !isDirty()) {
      return;
    }
    event.preventDefault();
    event.returnValue = state.labels.unsavedLeave;
  });
}

init();