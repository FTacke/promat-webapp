// ============================================
// Turbo Drive Integration für persistente Navigation
// ============================================
// Drawer-State bleibt erhalten bei Page-Wechseln
// Accordion öffnet/schließt OHNE Animation bei Route-Changes
// Diff-basiert: Nur Änderungen anwenden, kein Global-Reset

// Configure Turbo Progress Bar delay (show only after 200ms for short navigations)
if (window.Turbo && window.Turbo.config) {
  window.Turbo.config.drive.progressBarDelay = 200;
  console.log("[Turbo] Progress bar delay set to 200ms");
}

// Aktuell geöffnete Section tracken (persistent über Page-Wechsel)
let currentSection = null;

/**
 * Section aus URL-Pfad extrahieren
 * @param {string} pathname - URL pathname (z.B. /proyecto/diseno)
 * @returns {string|null} - Section name (z.B. 'proyecto') oder null
 */
function getSectionFromURL(pathname) {
  // Mapping: URL-Pfad → Section-ID
  if (pathname.startsWith("/proyecto")) return "proyecto";
  if (pathname.startsWith("/atlas")) return "atlas";
  if (pathname.startsWith("/corpus")) return "corpus";
  // Weitere Sections nach Bedarf
  return null;
}

/**
 * Pfad normalisieren für präzisen Vergleich
 * @param {string} href - URL oder Pfad
 * @returns {string} - Normalisierter Pfad
 */
function normalizePath(href) {
  try {
    const url = new URL(href, location.origin);
    let path = url.pathname;
    // Trailing Slash und index.html normalisieren
    path = path.replace(/\/index\.html$/i, "/");
    if (path.length > 1) {
      path = path.replace(/\/+$/, "");
    }
    return path;
  } catch (e) {
    return href;
  }
}

/**
 * Prüft ob Link aktiv ist basierend auf Match-Strategie
 * @param {HTMLAnchorElement} link - Link-Element
 * @param {string} currentPath - Aktueller normalisierter Pfad
 * @returns {boolean} - True wenn Link aktiv
 */
function isActiveLink(link, currentPath) {
  const linkPath = normalizePath(link.href);
  const matchType = link.dataset.match || "exact";

  if (matchType === "section") {
    // Parent-Link: Prefix-Regel für Unterseiten
    return currentPath.startsWith(linkPath);
  }

  // Standard: Exakte Übereinstimmung
  return linkPath === currentPath;
}

/**
 * Transitions temporär deaktivieren für instant state change
 * @param {Function} fn - Callback der während no-anim ausgeführt wird
 */
function setNoAnim(fn) {
  const drawer = document.getElementById("navigation-drawer");

  if (drawer) drawer.classList.add("no-anim");

  fn();

  requestAnimationFrame(() => {
    if (drawer) drawer.classList.remove("no-anim");
  });
}

/**
 * Accordion diff-basiert für Section öffnen/schließen
 * NUR ändern wenn nötig, NIE global reset
 * @param {string} section - Section name (z.B. 'proyecto') oder null
 */
function ensureAccordionFor(section) {
  currentSection = section;
}

/**
 * Highlight aktive Navigation basierend auf aktueller URL
 * Saubere ARIA-Implementierung: aria-current nur bei aktiven Links
 */
function highlightNavigationFromURL(pathname) {
  const drawer = document.getElementById("navigation-drawer");
  if (!drawer) return;

  const currentPath = normalizePath(pathname);

  // Reset aria-current on all links
  drawer.querySelectorAll("a[aria-current]").forEach((el) => {
    el.removeAttribute("aria-current");
  });

  // Mark active links
  drawer.querySelectorAll("a[href]").forEach((link) => {
    if (isActiveLink(link, currentPath)) {
      link.setAttribute("aria-current", "page");
    }
  });
}

/**
 * Mobilen Modal Drawer schließen vor Navigation
 */
function closeMobileDrawer() {
  const modalDrawer = document.getElementById("navigation-drawer-modal");
  if (modalDrawer && modalDrawer.open) {
    modalDrawer.close();
  }
}

/**
 * Turbo Drive Events für Navigation-Updates
 */
export function initTurboIntegration() {
  console.log("[Turbo Integration] Initializing...");

  const drawer = document.getElementById("navigation-drawer");

  // Hydration Guard: Transitions deaktivieren während Turbo-Render
  document.addEventListener("turbo:before-render", () => {
    console.log("[Turbo] Before render - activating hydration guard");
    drawer?.setAttribute("data-hydrating", "");
    document.body.setAttribute("data-hydrating", ""); // For focus suppression
  });

  document.addEventListener("turbo:render", () => {
    console.log("[Turbo] Render complete - deactivating hydration guard");
    // Nach Render genau einen Frame warten, dann wieder animierbar
    requestAnimationFrame(() => {
      drawer?.removeAttribute("data-hydrating");
      document.body.removeAttribute("data-hydrating");
    });
  });

  // Bei Page-Load: Section prüfen und Accordion diff-basiert anpassen
  document.addEventListener("turbo:load", () => {
    console.log(
      "[Turbo] turbo:load event fired, pathname:",
      window.location.pathname,
    );
    const section = getSectionFromURL(window.location.pathname);
    console.log("[Turbo] Detected section:", section);
    highlightNavigationFromURL(window.location.pathname); // Nur Link-Highlights
    ensureAccordionFor(section); // Diff-basiert: nur ändern wenn nötig

    // Focus management removed to prevent blue flash during navigation
    // Focus is only set on keyboard interaction in main.js
  });

  // Vor Navigation: Mobilen Drawer schließen
  document.addEventListener("turbo:before-visit", () => {
    closeMobileDrawer();
  });

  // Vor Turbo Cache: Cleanup flags
  document.addEventListener("turbo:before-cache", () => {
    console.log("[Turbo] Before cache - cleaning up hydration flags");
    drawer?.removeAttribute("data-hydrating");
    document.body.removeAttribute("data-hydrating");
  });

  // Optional: Progress-Indicator während Navigation
  document.addEventListener("turbo:before-visit", () => {
    document.body.classList.add("turbo-loading");
  });

  document.addEventListener("turbo:load", () => {
    document.body.classList.remove("turbo-loading");
  });

  document.addEventListener("turbo:visit", () => {
    document.body.classList.remove("turbo-loading");
  });

  // Initiales Setup
  const initialSection = getSectionFromURL(window.location.pathname);
  highlightNavigationFromURL(window.location.pathname);
  ensureAccordionFor(initialSection);

  console.log(
    "[Turbo Integration] Initialized with diff-based accordion and hydration guard",
  );
}
