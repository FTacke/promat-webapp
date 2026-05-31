// ============================================
// Navigation Drawer Controller - Dialog-basiert
// ============================================

import { getWindowSize, WindowSize } from "./window-size.js";
import { initSwipeGestures } from "./swipe-gestures.js";

/**
 * Focusable element selector
 */
const focusableSelectors =
  'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';

/**
 * Navigation Drawer Manager (Dialog-basiert)
 */
export class NavigationDrawer {
  constructor() {
    // Guard: Nur einmal initialisieren (für Turbo Drive)
    if (window.__drawerInit) {
      console.log("[Navigation Drawer] Already initialized, skipping");
      return window.__drawerInstance;
    }

    this.modalDrawer = document.getElementById("navigation-drawer-modal");
    this.standardDrawer = document.getElementById("navigation-drawer-standard");
    this.modalPanel = this.modalDrawer?.querySelector(".promat-panel--modal");
    this.openButton = document.querySelector('[data-action="open-drawer"]');
    this.mediaQuery = window.matchMedia("(max-width: 839px)");
    this.motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.isClosing = false;
    this.closeTimer = null;
    this.previousHtmlOverflow = "";
    this.previousBodyOverflow = "";

    if (!this.modalDrawer || !this.standardDrawer) {
      return;
    }

    this.init();
    this.swipeHandler = initSwipeGestures(this.modalDrawer, this.mediaQuery);

    // Globale Referenz speichern
    window.__drawerInit = true;
    window.__drawerInstance = this;
  }

  init() {
    // Open button
    if (this.openButton) {
      this.openButton.addEventListener("click", () => this.open());
    }

    // Klick ins Backdrop → schließen (Light Dismiss)
    this.modalDrawer.addEventListener("click", (e) => {
      if (e.target === this.modalDrawer) {
        this.close();
      }
    });

    // ESC wird von <dialog> automatisch gehandhabt via 'cancel' event
    // Aber wir können es auch explizit handlen für bessere Kontrolle
    this.modalDrawer.addEventListener("cancel", (e) => {
      e.preventDefault();
      this.close();
    });

    // Cleanup bei Resize: bei Expanded schließen
    this.mediaQuery.addEventListener("change", (e) => {
      if (!e.matches && this.modalDrawer.open) {
        this.close();
      }
    });

    // Handle links (close modal on navigation)
    this.modalDrawer.querySelectorAll("a[href]").forEach((link) => {
      link.addEventListener("click", () => {
        this.close();
      });
    });
  }

  queueSubmenuCleanup(submenu) {
    const finalize = () => {
      submenu.setAttribute("aria-hidden", "true");
      submenu.inert = true;
    };

    const duration = this.getTransitionDuration(submenu);
    if (duration === 0) {
      finalize();
      return;
    }

    let cleanedUp = false;
    const cleanup = (e) => {
      if (e && e.target !== submenu) return;
      if (cleanedUp) return;
      cleanedUp = true;
      submenu.removeEventListener("transitionend", cleanup);
      finalize();
    };

    submenu.addEventListener("transitionend", cleanup);
    window.setTimeout(() => cleanup(), duration + 40);
  }

  getTransitionDuration(element) {
    const styles = window.getComputedStyle(element);
    const durations = styles.transitionDuration.split(",");
    const delays = styles.transitionDelay.split(",");
    const toMs = (value) => {
      const trimmed = value.trim();
      if (!trimmed) return 0;
      if (trimmed.endsWith("ms")) return parseFloat(trimmed);
      if (trimmed.endsWith("s")) return parseFloat(trimmed) * 1000;
      return 0;
    };

    return durations.reduce((maxDuration, duration, index) => {
      const delay = delays[index] ?? delays[delays.length - 1] ?? "0s";
      return Math.max(maxDuration, toMs(duration) + toMs(delay));
    }, 0);
  }

  open() {
    // Only open modal drawer on Compact/Medium
    if (!this.mediaQuery.matches) return;

    if (this.isClosing) {
      this.finishClose();
    }

    // Native Dialog API: showModal() für Modalität + Fokus-Management
    if (!this.modalDrawer.open) {
      this.lastFocusedElement = document.activeElement;
      this.modalDrawer.showModal();
      this.modalDrawer.classList.remove("is-closing");

      requestAnimationFrame(() => {
        this.modalDrawer.classList.add("is-open");
      });

      // Set main content inert (blocks all interactions)
      const mainContent = document.querySelector("main");
      if (mainContent) {
        mainContent.inert = true;
      }

      this.setScrollLocked(true);

      // Focus the drawer shell, not the first link, to avoid a pointer-open focus ring.
      const drawerShell =
        this.modalDrawer.querySelector('[data-element="mobile-drawer-shell"]') ||
        this.modalDrawer.querySelector(focusableSelectors);
      if (drawerShell instanceof HTMLElement) {
        if (!drawerShell.hasAttribute("tabindex")) {
          drawerShell.setAttribute("tabindex", "-1");
        }
        setTimeout(() => drawerShell.focus({ preventScroll: true }), 100);
      }
    }

    // Update ARIA auf Open-Button
    if (this.openButton) {
      this.openButton.setAttribute("aria-expanded", "true");
    }
  }

  close() {
    if (!this.modalDrawer.open || this.isClosing) return;

    this.isClosing = true;
    this.modalDrawer.classList.remove("is-open");
    this.modalDrawer.classList.add("is-closing");

    const mainContent = document.querySelector("main");
    if (mainContent) {
      mainContent.inert = false;
    }

    const duration = this.motionQuery.matches
      ? 0
      : Math.max(
          this.getTransitionDuration(this.modalPanel || this.modalDrawer),
          this.getTransitionDuration(this.modalDrawer),
        );

    window.clearTimeout(this.closeTimer);
    if (duration === 0) {
      this.finishClose();
    } else {
      this.closeTimer = window.setTimeout(() => this.finishClose(), duration + 40);
    }

    // Update ARIA auf Open-Button
    if (this.openButton) {
      this.openButton.setAttribute("aria-expanded", "false");
    }
  }

  finishClose() {
    if (!this.modalDrawer.open) {
      this.isClosing = false;
      return;
    }

    this.modalDrawer.close();
    this.modalDrawer.classList.remove("is-open", "is-closing");
    this.isClosing = false;
    this.setScrollLocked(false);

    if (this.openButton) {
      this.openButton.focus({ preventScroll: true });
    }
  }

  setScrollLocked(locked) {
    if (locked) {
      this.previousHtmlOverflow = document.documentElement.style.overflow;
      this.previousBodyOverflow = document.body.style.overflow;
      document.documentElement.style.overflow = "hidden";
      document.body.style.overflow = "hidden";
      return;
    }

    document.documentElement.style.overflow = this.previousHtmlOverflow;
    document.body.style.overflow = this.previousBodyOverflow;
  }
}

/**
 * Initialize navigation drawer
 */
export function initNavigationDrawer() {
  return new NavigationDrawer();
}
