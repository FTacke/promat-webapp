// ============================================
// Top App Bar Controller - User Menu Handler
// ============================================

const SUPPORTED_UI_LANGS = new Set(["de", "en"]);
const UI_LANG_PATH_PATTERN = /^\/(de|en)(?=\/|$)/;

function resolveBaseOrigin(baseOrigin = null) {
  if (baseOrigin) {
    return baseOrigin;
  }
  if (typeof window !== "undefined" && window.location && window.location.origin) {
    return window.location.origin;
  }
  return "http://localhost";
}

function resolveUiLang(targetUiLang) {
  return SUPPORTED_UI_LANGS.has(targetUiLang) ? targetUiLang : "de";
}

function pathHasUiLangPrefix(pathname) {
  return UI_LANG_PATH_PATTERN.test(pathname || "");
}

function swapUiLangPrefix(pathname, targetUiLang) {
  if (!pathHasUiLangPrefix(pathname)) {
    return pathname || "/";
  }
  return (pathname || "/").replace(UI_LANG_PATH_PATTERN, `/${resolveUiLang(targetUiLang)}`);
}

function currentUiLangFromLocation(currentHref = null, baseOrigin = null) {
  const origin = resolveBaseOrigin(baseOrigin);
  const currentUrl = new URL(currentHref || origin, origin);
  const matchedPath = currentUrl.pathname.match(UI_LANG_PATH_PATTERN);
  if (matchedPath) {
    return resolveUiLang(matchedPath[1]);
  }
  const queryUiLang = currentUrl.searchParams.get("lang") || currentUrl.searchParams.get("ui_lang") || "";
  if (SUPPORTED_UI_LANGS.has(queryUiLang)) {
    return queryUiLang;
  }
  if (typeof document !== "undefined") {
    const htmlLang = document.documentElement.getAttribute("data-ui-lang") || document.documentElement.lang || "";
    if (SUPPORTED_UI_LANGS.has(htmlLang)) {
      return htmlLang;
    }
  }
  return "de";
}

function rewriteLocalUiLangUrl(rawUrl, targetUiLang, baseOrigin = null) {
  if (!rawUrl) {
    return rawUrl;
  }

  const normalizedUiLang = resolveUiLang(targetUiLang);
  const origin = resolveBaseOrigin(baseOrigin);

  let parsed;
  try {
    parsed = new URL(rawUrl, origin);
  } catch {
    return rawUrl;
  }

  if (parsed.origin !== origin) {
    return rawUrl;
  }

  const rewrittenPath = pathHasUiLangPrefix(parsed.pathname)
    ? swapUiLangPrefix(parsed.pathname, normalizedUiLang)
    : (parsed.pathname || "/");
  const searchParams = new URLSearchParams(parsed.search);
  searchParams.delete("ui_lang");
  searchParams.delete("lang");
  if (searchParams.has("next")) {
    const nextValue = searchParams.get("next") || "";
    searchParams.set("next", rewriteLocalUiLangUrl(nextValue, normalizedUiLang, origin) || nextValue);
  }

  const query = searchParams.toString();
  return `${rewrittenPath}${query ? `?${query}` : ""}${parsed.hash || ""}`;
}

export function buildUiLangSwitchUrl(targetUiLang, currentHref = null, baseOrigin = null) {
  const normalizedUiLang = resolveUiLang(targetUiLang);
  const origin = resolveBaseOrigin(baseOrigin);
  const fallbackHref = typeof window !== "undefined" && window.location ? window.location.href : origin;
  const currentUrl = new URL(currentHref || fallbackHref, origin);
  const searchParams = new URLSearchParams(currentUrl.search);

  searchParams.delete("ui_lang");
  searchParams.delete("lang");
  if (searchParams.has("next")) {
    const nextValue = searchParams.get("next") || "";
    searchParams.set("next", rewriteLocalUiLangUrl(nextValue, normalizedUiLang, origin) || nextValue);
  }

  const localizedPath = pathHasUiLangPrefix(currentUrl.pathname)
    ? swapUiLangPrefix(currentUrl.pathname, normalizedUiLang)
    : (currentUrl.pathname || "/");
  searchParams.set("lang", normalizedUiLang);

  const query = searchParams.toString();
  return `${localizedPath}${query ? `?${query}` : ""}${currentUrl.hash || ""}`;
}

function dispatchPromatLocationChange() {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(new CustomEvent("promat:locationchange", {
    detail: { href: window.location.href },
  }));
}

function installLocationChangeEmitter() {
  if (typeof window === "undefined" || window.__promatLocationChangeEmitterInstalled) {
    return;
  }
  window.__promatLocationChangeEmitterInstalled = true;

  ["pushState", "replaceState"].forEach((methodName) => {
    const original = window.history[methodName];
    if (typeof original !== "function") {
      return;
    }
    window.history[methodName] = function patchedHistoryMethod(...args) {
      const result = original.apply(this, args);
      dispatchPromatLocationChange();
      return result;
    };
  });

  window.addEventListener("popstate", dispatchPromatLocationChange);
}

function syncLanguageSwitchLinks() {
  if (typeof document === "undefined") {
    return;
  }

  const currentUiLang = currentUiLangFromLocation(typeof window !== "undefined" ? window.location.href : null);
  document.querySelectorAll("[data-ui-lang-link]").forEach((link) => {
    const targetUiLang = resolveUiLang(link.dataset.uiLangLink || "de");
    link.setAttribute("href", buildUiLangSwitchUrl(targetUiLang));

    const isCurrent = targetUiLang === currentUiLang;
    link.classList.toggle("is-active", isCurrent);
    if (isCurrent) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
}

function initLanguageSwitchSync() {
  if (typeof document === "undefined" || window.__promatLanguageSwitchSyncInit) {
    return;
  }
  window.__promatLanguageSwitchSyncInit = true;

  installLocationChangeEmitter();

  document.addEventListener("click", (event) => {
    const languageLink = event.target.closest("[data-ui-lang-link]");
    if (!languageLink) {
      return;
    }
    languageLink.setAttribute("href", buildUiLangSwitchUrl(languageLink.dataset.uiLangLink || "de"));
  });

  document.addEventListener("turbo:load", syncLanguageSwitchLinks);
  window.addEventListener("pageshow", syncLanguageSwitchLinks);
  window.addEventListener("promat:locationchange", syncLanguageSwitchLinks);

  syncLanguageSwitchLinks();
}

/**
 * Initialize User Menu Toggle
 *
 * Handles opening/closing of avatar dropdown menu.
 * Uses delegated event listeners to work on every page load.
 * Binds on DOMContentLoaded to ensure DOM is ready.
 */
function syncUserMenuState(toggle, dropdown, open) {
  if (!toggle || !dropdown) {
    return;
  }
  toggle.setAttribute("aria-expanded", open ? "true" : "false");
  dropdown.hidden = !open;
  if (open) {
    dropdown.setAttribute("data-open", "");
  } else {
    dropdown.removeAttribute("data-open");
  }
}

function focusFirstUserMenuItem(dropdown) {
  const firstItem = dropdown.querySelector('[role="menuitem"]');
  if (firstItem) {
    window.setTimeout(() => firstItem.focus(), 50);
  }
}

function bindUserMenu(userMenuRoot) {
  if (!userMenuRoot) {
    return null;
  }

  const toggle = userMenuRoot.querySelector("[data-account-menu-trigger], [data-user-menu-toggle]");
  const dropdown = userMenuRoot.querySelector("[data-user-menu]");

  if (!toggle || !dropdown) {
    return null;
  }

  const closeMenu = () => {
    syncUserMenuState(toggle, dropdown, false);
  };
  const openMenu = () => {
    syncUserMenuState(toggle, dropdown, true);
    focusFirstUserMenuItem(dropdown);
  };

  closeMenu();

  if (userMenuRoot.dataset.userMenuBound === "true") {
    return { toggle, dropdown, closeMenu, openMenu };
  }

  userMenuRoot.dataset.userMenuBound = "true";

  toggle.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    const isExpanded = toggle.getAttribute("aria-expanded") === "true";
    if (isExpanded) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (!userMenuRoot.contains(event.target)) {
      closeMenu();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
      closeMenu();
      toggle.focus();
    }
  });

  document.addEventListener("turbo:before-visit", closeMenu);
  document.addEventListener("turbo:load", closeMenu);
  window.addEventListener("pageshow", closeMenu);
  window.addEventListener("pagehide", closeMenu);
  window.addEventListener("popstate", closeMenu);

  dropdown.querySelectorAll('[role="menuitem"]').forEach((item) => {
    item.addEventListener("click", closeMenu);
  });

  return { toggle, dropdown, closeMenu, openMenu };
}

function initUserMenu() {
  const userMenuRoot = document.querySelector("[data-user-menu-root]");
  if (!bindUserMenu(userMenuRoot)) {
    console.log("[TopAppBar] User menu not found on this page");
    return;
  }

  console.log("[TopAppBar] User menu initialized");
}

/**
 * Top App Bar Manager (Legacy - kept for compatibility)
 * - Transparent, Elevation 0
 * - Burger links (nur Compact/Medium)
 * - Login/Avatar rechts
 * - User Menu mit Logout
 * - Login redirect (MD3 Goldstandard: full-page login)
 */
export class TopAppBar {
  constructor() {
    // Prevent double-instantiation across different initializers
    if (window.__topAppBarInit) return window.__topAppBarInstance;

    this.appBar = document.querySelector('[data-element="top-app-bar"]');

    if (!this.appBar) {
      return;
    }

    this.init();
  }

  init() {
    // User menu functionality
    initUserMenu();

    // Keep language-switch targets aligned with the live URL and workbench state.
    initLanguageSwitchSync();

    // Login handler (MD3 Goldstandard: full-page login)
    this.initLoginHandler();

    // Optional: Check for ?showlogin=1 query parameter
    this.checkAutoOpenLogin();
  }

  /**
   * Login redirect handler
   * MD3 Goldstandard: Login is always full-page, no sheet overlay
   */
  initLoginHandler() {
    // "open-login" buttons now navigate to full-page login
    const openButtons = document.querySelectorAll('[data-action="open-login"]');
    openButtons.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        // Get current URL as next parameter for redirect after login
        const currentUrl = window.location.pathname + window.location.search;
        window.location.href = `/login?next=${encodeURIComponent(currentUrl)}`;
      });
    });
  }

  /**
   * Auto-redirect to login if ?showlogin=1 in URL
   * MD3 Goldstandard: Redirect to /login with next parameter
   */
  checkAutoOpenLogin() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("showlogin") === "1") {
      // Build clean next URL (without showlogin param)
      const url = new URL(window.location);
      url.searchParams.delete("showlogin");
      const nextUrl = url.pathname + url.search;
      
      // Redirect to full-page login
      window.location.href = `/login?next=${encodeURIComponent(nextUrl)}`;
    }
  }
}

/**
 * Initialize top app bar
 */
export function initTopAppBar() {
  const inst = new TopAppBar();
  if (!window.__topAppBarInit) {
    window.__topAppBarInit = true;
    window.__topAppBarInstance = inst;
  }
  return inst;
}

// Export delegated user menu initializer
export { initUserMenu };
