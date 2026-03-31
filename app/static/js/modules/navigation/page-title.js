// ============================================
// Page Title Module (Framework-agnostisch)
// ============================================
// Bestimmt Seitentitel aus mehreren Quellen
// und synchronisiert sie optional mit einem Title-Zielelement im DOM
// Events: DOMContentLoaded, htmx:*, turbo:*, popstate

const TITLE_TEXT = "Pronunciation Matters";

/**
 * Titel in DOM anwenden und document.title aktualisieren
 */
function applyTitle() {
  const title = TITLE_TEXT;

  // Optionales Ziel-Element fuer eine im DOM sichtbare Seitentitel-Zone
  const pageTitleEl = document.querySelector("[data-page-title-el], #pageTitle");
  if (pageTitleEl) {
    pageTitleEl.textContent = title;
  }

  document.title = title;
}

/**
 * MutationObserver für Live-Änderungen im <main>
 */
let observer = null;

function setupObserver() {
  const main = document.querySelector("main");
  if (!main) return;

  // Alten Observer deaktivieren
  if (observer) {
    observer.disconnect();
  }

  // Neuer Observer mit Debounce
  let timeoutId = null;
  observer = new MutationObserver(() => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      console.log("[Page Title] Mutation detected in main");
      applyTitle();
    }, 50);
  });

  observer.observe(main, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: false,
  });

  console.log("[Page Title] Observer mounted");
}

/**
 * Exports
 */
export function initPageTitle() {
  if (window.__pageTitleInit) {
    console.log("[Page Title] Already initialized, skipping");
    return;
  }
  window.__pageTitleInit = true;

  console.log("[Page Title] Initializing...");

  // Initial anwenden
  applyTitle();
  setupObserver();

  // Event Handler - nur einmal registrieren
  const handleNav = () => {
    console.log("[Page Title] Navigation event");
    applyTitle();
    setupObserver(); // Observer nach Swap neu aufbauen
  };

  // Standard: DOMContentLoaded (bei erster Ladung)
  document.addEventListener("DOMContentLoaded", handleNav, { once: true });

  // HTMX Events
  if (window.htmx) {
    document.body.addEventListener("htmx:afterSwap", handleNav);
    document.body.addEventListener("htmx:afterSettle", handleNav);
    document.body.addEventListener("htmx:historyRestore", handleNav);
  }

  // Turbo Events
  if ("Turbo" in window) {
    document.addEventListener("turbo:render", handleNav);
  }

  // Browser Back/Forward
  window.addEventListener("popstate", handleNav);

  // Fallback: pageshow (bfcache)
  window.addEventListener("pageshow", handleNav);

  console.log("[Page Title] ✅ Initialized");
}

// Auto-Init wenn direkt als Script geladen
try {
  initPageTitle();
} catch (e) {
  console.warn("[Page Title] Auto-init failed:", e);
}
