// ============================================
// Top App Bar Controller - User Menu Handler
// ============================================

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
      console.warn("[TopAppBar] App Bar not found");
      return;
    }

    this.init();
  }

  init() {
    // User menu functionality
    initUserMenu();

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
