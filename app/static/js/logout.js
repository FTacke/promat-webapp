/*
 * Logout helper
 * - Intercepts clicks on elements with data-logout="fetch" and performs
 *   a fetch request to the logout endpoint, then refreshes the UI using
 *   window.location.reload()
 * - Logout is a state-changing POST (CSRF-protected on the server); there is no GET fallback.
 */

(function () {
  if (typeof window === 'undefined') return;
  // Avoid double-binding click handlers if script runs multiple times
  if (window.__logoutInit) return;
  window.__logoutInit = true;

  function performLogout(el) {
    const url = el.dataset.logoutUrl || '/auth/logout';
    const method = 'POST';

    // Try to obtain a CSRF token helper if available
    const token = (window.authSetup && window.authSetup.getCSRFToken) ? window.authSetup.getCSRFToken() : null;

    const opts = {
      method: method,
      credentials: 'same-origin',
      headers: {},
    };

    if (token) {
      opts.headers['X-CSRF-Token'] = token;
    }

    // Add a safety timeout so the UI doesn't hang when fetch hangs or server is slow.
    const fetchWithTimeout = (resource, options = {}, timeout = 3000) => {
      return Promise.race([
        fetch(resource, options),
        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), timeout))
      ]);
    };

    return fetchWithTimeout(url, opts, 3000)
      .then((res) => {
        // If server uses HTMX-style redirect headers prefer that value
        const hxRedirect = res.headers && res.headers.get && res.headers.get('HX-Redirect');
        if (hxRedirect) {
          window.location.href = hxRedirect;
          return;
        }
        // A rejected request (for example a failed CSRF check) did not sign the user out: stay on the page state
        // the server reports instead of pretending the logout worked.
        if (!res.ok) {
          window.location.reload();
          return;
        }
        // Prefer server-sent redirect URL when present, otherwise present the logged-out landing page.
        window.location.href = res.redirected && res.url ? res.url : '/';
      })
      .catch((err) => {
        console.error('[Logout] Failed', err);
        window.location.reload();
      });
  }

  function onClick(e) {
    const el = e.target.closest && e.target.closest('[data-logout="fetch"]');
    if (!el) return;

    e.preventDefault();
    performLogout(el);
  }

  document.addEventListener('click', onClick, { passive: false });

  // Find initial elements and make them accessible for assistive tech
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-logout="fetch"]').forEach(function (el) {
      el.setAttribute('role', el.getAttribute('role') || 'button');
      el.setAttribute('tabindex', el.getAttribute('tabindex') || '0');
    });
  });

  // Expose helper for tests
  window.CORAPAN = window.CORAPAN || {};
  window.CORAPAN.logout = performLogout;

})();
