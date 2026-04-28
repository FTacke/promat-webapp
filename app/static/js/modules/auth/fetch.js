/**
 * Minimal authenticated fetch helper for cookie-based auth.
 *
 * PROMAT currently uses a server-driven JWT cookie flow without a client-side
 * refresh loop. This wrapper only applies the canonical request defaults.
 */

export async function fetchWithAuth(url, options = {}) {
  return fetch(url, {
    ...options,
    credentials: options.credentials || "same-origin",
    cache: options.cache || "no-store",
  });
}