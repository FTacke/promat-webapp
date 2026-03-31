/**
 * Global Configuration
 * Reads configuration from data-config attribute on body.
 */

export function initConfig() {
  const body = document.body;
  const configData = body.getAttribute('data-config');
  const target = {};
  
  if (configData) {
    try {
      const config = JSON.parse(configData);
      Object.assign(target, config);
    } catch (e) {
      console.error('[Config] Failed to parse global config:', e);
    }
  }

  window.__PROMAT__ = target;
  window.__CORAPAN__ = target;
}
