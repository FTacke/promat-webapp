/**
 * CO.RA.PAN Authentication Setup
 *
 * Ensures cookies are sent with all fetch requests and handles
 * authentication-specific behavior.
 *
 * This script MUST load before other app scripts.
 */

// =============================================================================
// 1. Intercept all fetch() calls to include credentials
// =============================================================================

const originalFetch = window.fetch;

window.fetch = function (resource, config = {}) {
  // Ensure credentials are sent with same-origin requests
  // This is CRITICAL for cookies to be included in requests
  if (!config.credentials) {
    config.credentials = "same-origin";
  }

  return originalFetch(resource, config);
};

// =============================================================================
// 2. Disable Turbo for authentication-related forms
// =============================================================================

// Disable Turbo for login form to ensure clean page reload with cookies
document.addEventListener("turbo:before-fetch-request", (event) => {
  const url = event.detail.fetchOptions.url || "";

  if (url.includes("/auth/login") || url.includes("/login")) {
    // Force full page reload for login (don't use Turbo cache)
    event.detail.fetchOptions.headers = event.detail.fetchOptions.headers || {};
    event.detail.fetchOptions.headers["Turbo-Force-Full-Page-Load"] = "true";
  }
});

// Also disable Turbo for form submissions on /auth/login
document.addEventListener("turbo:submit-start", (event) => {
  const form = event.detail.formSubmission.form;
  if (form && form.action && (form.action.includes("/auth/login") || form.action.includes("/login"))) {
    form.setAttribute("data-turbo", "false");
  }
});

// Alternative: Mark login form with data-turbo="false" on page load
document.addEventListener("turbo:load", () => {
  const loginForms = document.querySelectorAll('form[action*="/auth/login"], form[action*="/login"]');
  loginForms.forEach((form) => {
    form.setAttribute("data-turbo", "false");
  });
});

// =============================================================================
// 3. Helper: Get CSRF token for mutating requests
// =============================================================================

window.getCSRFToken = function (tokenName = "csrf_access_token") {
  // Extract CSRF token from cookie
  const name = tokenName + "=";
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(";");

  for (let cookie of cookieArray) {
    cookie = cookie.trim();
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length);
    }
  }

  return null;
};

// =============================================================================
// Export for use in other scripts
// =============================================================================
// The former "verify authentication on page load" request (GET /auth/session on every page) had no consumer:
// authentication state is rendered by the server, so it was removed.

window.authSetup = {
  getCSRFToken: window.getCSRFToken,
};
