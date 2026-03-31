/**
 * Compatibility entry point for legacy shell bootstrapping.
 *
 * The modular core still imports this file. Keep it small and delegate to the
 * current navigation and auth-refresh modules so older import paths continue to work.
 */

import "./modules/navigation/index.js";
import { initAuthRefresh } from "./modules/auth/refresh.js";

if (!window.__promatLegacyMainInit) {
  window.__promatLegacyMainInit = true;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      initAuthRefresh();
    });
  } else {
    initAuthRefresh();
  }
}