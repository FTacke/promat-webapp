import { getCsrfToken } from "../api.js";
import { fetchWithAuth } from "../modules/auth/fetch.js";
import { showSnackbar } from "../modules/core/snackbar.js";
import { initOverflowMenus } from "../modules/core/overflow-menu.js";

let requestFailedLabel = "";

function parseState() {
  const element = document.getElementById("pm-phenomena-overview-state");
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

function init() {
  const state = parseState();
  const root = document.querySelector("[data-phenomena-overview-root]");
  if (!state || !root) {
    return;
  }
  requestFailedLabel = state.labels?.requestFailed || requestFailedLabel;

  const searchInput = root.querySelector("[data-phenomena-search]");
  const listShell = root.querySelector("[data-phenomena-list-shell]");
  const list = root.querySelector("[data-phenomena-entry-list]");
  const emptyState = root.querySelector("[data-phenomena-empty-state]");
  const emptyTitle = root.querySelector("[data-phenomena-empty-title]");
  const emptyText = root.querySelector("[data-phenomena-empty-text]");
  const newListButton = root.querySelector("[data-phenomena-new-set]");
  const renameDialog = document.querySelector("[data-phenomena-rename-dialog]");
  const renameForm = document.querySelector("[data-phenomena-rename-form]");
  const renameInput = document.querySelector("[data-phenomena-rename-input]");
  const renameError = document.querySelector("[data-phenomena-rename-error]");
  const renameCancel = document.querySelector("[data-phenomena-rename-cancel]");
  const deleteDialog = document.querySelector("[data-phenomena-delete-dialog]");
  const deleteObject = document.querySelector("[data-phenomena-delete-object]");
  const deleteCancel = document.querySelector("[data-phenomena-delete-cancel]");
  const deleteConfirm = document.querySelector("[data-phenomena-delete-confirm]");

  let renameTargetId = null;
  let deleteTargetId = null;
  let pending = false;

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

  function resetRenameDialog() {
    renameTargetId = null;
    if (renameError) {
      renameError.hidden = true;
      renameError.textContent = "";
    }
  }

  function resetDeleteDialog() {
    deleteTargetId = null;
    if (deleteObject) {
      deleteObject.textContent = "";
    }
  }

  function closePhenomenaDialogs() {
    closeDialog(renameDialog);
    closeDialog(deleteDialog);
  }

  function entryCards() {
    return Array.from(root.querySelectorAll("[data-phenomena-entry]"));
  }

  function closeDetailsMenus() {
    root.querySelectorAll("details[data-overflow-menu]").forEach((element) => {
      element.open = false;
    });
  }

  function applyFilter() {
    const term = (searchInput?.value || "").trim().toLowerCase();
    const hasBaseEntries = Array.isArray(state.entries) && state.entries.length > 0;
    let visibleCount = 0;
    entryCards().forEach((card) => {
      const haystack = `${card.dataset.title || ""}`;
      const visible = !term || haystack.includes(term);
      card.hidden = !visible;
      if (visible) {
        visibleCount += 1;
      }
    });
    if (emptyState) {
      emptyState.hidden = visibleCount > 0;
      if (emptyTitle) {
        emptyTitle.textContent = hasBaseEntries ? (state.labels?.emptyTitle || "") : (state.labels?.noDataTitle || "");
      }
      if (emptyText) {
        const nextText = hasBaseEntries ? (state.labels?.emptyText || "") : (state.labels?.noDataText || "");
        emptyText.textContent = nextText;
        emptyText.hidden = !nextText;
      }
    }
    if (listShell) {
      listShell.hidden = visibleCount === 0;
    }
  }

  function updateCardLabel(setId, label) {
    const card = root.querySelector(`[data-kind="custom"] [data-phenomena-rename-set="${CSS.escape(setId)}"]`)?.closest("[data-phenomena-entry]");
    if (!card) {
      return;
    }
    const titleNode = card.querySelector("[data-phenomena-entry-title]");
    if (titleNode) {
      titleNode.textContent = label;
    }
    card.dataset.title = label.toLowerCase();
  }

  async function createList(payload) {
    if (pending) {
      return;
    }
    if (!state.isAuthenticated && state.loginHref) {
      window.location.href = state.loginHref;
      return;
    }
    pending = true;
    try {
      const response = await requestJson(state.createSetUrl, {
        method: "POST",
        body: {
          corpus_language: state.languageSlug,
          ...payload,
        },
      });
      const setId = response?.set?.set_id;
      if (!setId) {
        throw new Error(state.labels.createError);
      }
      window.location.href = buildUrl(state.setEditorHrefTemplate, setId);
    } catch (error) {
      showSnackbar(error.message || state.labels.createError, "error");
    } finally {
      pending = false;
    }
  }

  async function openOwnCopy(sourceSetId) {
    if (pending) {
      return;
    }
    if (!state.isAuthenticated && state.loginHref) {
      window.location.href = state.loginHref;
      return;
    }
    pending = true;
    try {
      const response = await requestJson(buildUrl(state.privateCopySetUrlTemplate, sourceSetId), {
        method: "POST",
        body: { lifecycle: "draft" },
      });
      const setId = response?.set?.set_id;
      if (!setId) {
        throw new Error(state.labels.createError);
      }
      window.location.href = buildUrl(state.setEditorHrefTemplate, setId);
    } catch (error) {
      showSnackbar(error.message || state.labels.createError, "error");
    } finally {
      pending = false;
    }
  }

  function openRenameDialog(setId, currentLabel) {
    renameTargetId = setId;
    if (renameInput) {
      renameInput.value = currentLabel || "";
    }
    if (renameError) {
      renameError.hidden = true;
      renameError.textContent = "";
    }
    showDialog(renameDialog);
  }

  function openDeleteDialog(setId, label) {
    deleteTargetId = setId;
    if (deleteObject) {
      deleteObject.textContent = label || state.labels.untitled;
    }
    showDialog(deleteDialog);
  }

  newListButton?.addEventListener("click", () => {
    createList({});
  });

  searchInput?.addEventListener("input", applyFilter);

  root.addEventListener("click", (event) => {
    const copyButton = event.target.closest("[data-phenomena-copy-curated-set]");
    if (copyButton) {
      event.preventDefault();
      openOwnCopy(copyButton.dataset.phenomenaCopyCuratedSet);
      return;
    }

    const renameButton = event.target.closest("[data-phenomena-rename-set]");
    if (renameButton) {
      event.preventDefault();
      closeDetailsMenus();
      const card = renameButton.closest("[data-phenomena-entry]");
      const currentLabel = card?.querySelector("[data-phenomena-entry-title]")?.textContent?.trim() || "";
      openRenameDialog(renameButton.dataset.phenomenaRenameSet, currentLabel);
      return;
    }

    const deleteButton = event.target.closest("[data-phenomena-delete-set]");
    if (deleteButton) {
      event.preventDefault();
      closeDetailsMenus();
      const card = deleteButton.closest("[data-phenomena-entry]");
      const label = card?.querySelector("[data-phenomena-entry-title]")?.textContent?.trim() || "";
      openDeleteDialog(deleteButton.dataset.phenomenaDeleteSet, label);
    }
  });

  renameCancel?.addEventListener("click", () => closeDialog(renameDialog));
  deleteCancel?.addEventListener("click", () => closeDialog(deleteDialog));

  renameDialog?.addEventListener("close", resetRenameDialog);
  deleteDialog?.addEventListener("close", resetDeleteDialog);

  renameForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!renameTargetId || pending) {
      return;
    }
    pending = true;
    if (renameError) {
      renameError.hidden = true;
      renameError.textContent = "";
    }
    try {
      const response = await requestJson(buildUrl(state.patchSetUrlTemplate, renameTargetId), {
        method: "PATCH",
        body: { label: renameInput?.value || "" },
      });
      const label = response?.set?.label || (renameInput?.value || "").trim();
      updateCardLabel(renameTargetId, label);
      closeDialog(renameDialog);
      applyFilter();
      showSnackbar(state.labels.renameSuccess, "success");
    } catch (error) {
      if (renameError) {
        renameError.hidden = false;
        renameError.textContent = error.message || state.labels.createError;
      }
    } finally {
      pending = false;
    }
  });

  deleteConfirm?.addEventListener("click", async () => {
    if (!deleteTargetId || pending) {
      return;
    }
    pending = true;
    try {
      await requestJson(buildUrl(state.deleteSetUrlTemplate, deleteTargetId), {
        method: "DELETE",
      });
      const card = root.querySelector(`[data-kind="custom"] [data-phenomena-delete-set="${CSS.escape(deleteTargetId)}"]`)?.closest("[data-phenomena-entry]");
      card?.remove();
      closeDialog(deleteDialog);
      applyFilter();
      showSnackbar(state.labels.deleteSuccess, "success");
    } catch (error) {
      showSnackbar(error.message || state.labels.delete, "error");
    } finally {
      pending = false;
    }
  });

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) {
      return;
    }
    const link = target.closest("a[href]");
    if (!link || link.closest("dialog")) {
      return;
    }
    const rawHref = link.getAttribute("href") || "";
    if (!rawHref || rawHref.startsWith("#") || rawHref.startsWith("javascript:") || rawHref.startsWith("mailto:") || rawHref.startsWith("tel:")) {
      return;
    }
    closePhenomenaDialogs();
  }, true);

  window.addEventListener("pagehide", closePhenomenaDialogs);
  window.addEventListener("beforeunload", closePhenomenaDialogs);

  initOverflowMenus();
  applyFilter();
}

init();