export function initAdmonitions(root = document) {
  if (!root || typeof root.querySelectorAll !== "function") {
    return;
  }

  const toggleButtons = root.querySelectorAll("[data-admonition-toggle]");
  toggleButtons.forEach((button) => {
    if (button.dataset.admonitionBound === "true") {
      return;
    }

    const panelId = button.getAttribute("aria-controls");
    if (!panelId) {
      return;
    }

    const panel = document.getElementById(panelId);
    if (!panel) {
      return;
    }

    const admonitionRoot = button.closest("[data-admonition]");
    const syncState = (expanded) => {
      button.setAttribute("aria-expanded", expanded ? "true" : "false");
      if (expanded) {
        panel.removeAttribute("hidden");
      } else {
        panel.setAttribute("hidden", "");
      }
      if (admonitionRoot) {
        admonitionRoot.dataset.admonitionOpen = expanded ? "true" : "false";
      }
    };

    syncState(button.getAttribute("aria-expanded") === "true");
    button.addEventListener("click", () => {
      syncState(button.getAttribute("aria-expanded") !== "true");
    });
    button.dataset.admonitionBound = "true";
  });
}