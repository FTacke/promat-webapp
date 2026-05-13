function fallbackCopyText(text) {
  const tempTextArea = document.createElement("textarea");
  tempTextArea.value = text;
  tempTextArea.setAttribute("readonly", "readonly");
  tempTextArea.style.position = "fixed";
  tempTextArea.style.left = "-9999px";
  document.body.appendChild(tempTextArea);
  tempTextArea.select();

  let copied = false;
  try {
    copied = document.execCommand("copy");
  } finally {
    document.body.removeChild(tempTextArea);
  }

  return copied;
}

async function copyText(text) {
  if (!text.trim()) {
    return false;
  }
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return fallbackCopyText(text);
    }
  }
  return fallbackCopyText(text);
}

export function initTeachingCitationCopy(root = document) {
  root.querySelectorAll("[data-copy-text]").forEach((button) => {
    if (button.dataset.citationCopyInitialized === "true") {
      return;
    }
    button.dataset.citationCopyInitialized = "true";

    const defaultLabel = button.dataset.copyDefaultLabel || button.getAttribute("aria-label") || "";
    const status = button.parentElement?.querySelector("[data-citation-copy-status]");
    let resetTimer = null;

    const setState = (state, label, message) => {
      button.dataset.copyState = state;
      button.setAttribute("aria-label", label);
      button.setAttribute("title", label);
      if (status) {
        status.textContent = "";
        window.requestAnimationFrame(() => {
          status.textContent = message;
        });
      }
      window.clearTimeout(resetTimer);
      resetTimer = window.setTimeout(() => {
        delete button.dataset.copyState;
        button.setAttribute("aria-label", defaultLabel);
        button.setAttribute("title", defaultLabel);
        if (status) {
          status.textContent = "";
        }
      }, 1800);
    };

    button.addEventListener("click", async () => {
      const didCopy = await copyText(button.dataset.copyText || "");
      if (didCopy) {
        setState(
          "done",
          button.dataset.copyCopiedLabel || button.dataset.copySuccess || defaultLabel,
          button.dataset.copySuccess || defaultLabel,
        );
        return;
      }
      setState(
        "error",
        button.dataset.copyError || defaultLabel,
        button.dataset.copyError || defaultLabel,
      );
    });
  });
}
