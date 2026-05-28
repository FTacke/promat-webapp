/**
 * Shared behaviour for disclosure-based overflow menus.
 *
 * Any <details data-overflow-menu> element in the document gets:
 * - Close when clicking outside the element.
 * - Close on Escape (focus returns to the summary).
 * - Only one menu open at a time (opening one closes all others).
 * - Close when an action button/link inside the menu is activated.
 *
 * aria-expanded is managed automatically by the browser for details/summary.
 *
 * Call initOverflowMenus() once per page (e.g. in the page's init function).
 */
export function initOverflowMenus() {
  // Outside-click and action-click: close relevant menus.
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) {
      return;
    }
    document.querySelectorAll("details[data-overflow-menu]").forEach((details) => {
      if (!details.open) {
        return;
      }
      if (!details.contains(target)) {
        // Click is outside this menu → close it.
        details.open = false;
      } else if (!target.closest("summary") && target.closest("button, a[href]")) {
        // Click is on an action inside the menu (not the toggle) → close after action.
        details.open = false;
      }
    });
  });

  // Escape key: close all open menus and return focus to their toggle.
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
      return;
    }
    document.querySelectorAll("details[data-overflow-menu]").forEach((details) => {
      if (!details.open) {
        return;
      }
      details.open = false;
      details.querySelector("summary")?.focus();
    });
  });

  // Ensure only one menu is open at a time (capture phase to run before toggle completes).
  document.addEventListener("toggle", (event) => {
    const details = event.target;
    if (!(details instanceof HTMLDetailsElement) || !details.hasAttribute("data-overflow-menu") || !details.open) {
      return;
    }
    document.querySelectorAll("details[data-overflow-menu]").forEach((other) => {
      if (other !== details && other.open) {
        other.open = false;
      }
    });
  }, true);
}
