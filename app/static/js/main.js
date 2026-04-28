/**
 * Compatibility entry point for legacy shell bootstrapping.
 *
 * Keep this small and limited to shared shell behavior.
 */

import "./modules/navigation/index.js";

if (!window.__promatLegacyMainInit) {
  window.__promatLegacyMainInit = true;
}