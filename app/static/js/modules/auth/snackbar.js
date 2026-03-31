/**
 * MD3 Snackbar Module - Auth Expiration Notification
 *
 * Shows Material Design 3 Snackbar when refresh token expires.
 */

/**
 * Show MD3 Snackbar for expired session
 * Persists until user interacts (no auto-dismiss)
 */
export function showAuthExpiredSnackbar() {
  // Check if snackbar already exists
  if (document.querySelector(".md3-snackbar--auth-expired")) {
    return; // Don't show multiple snackbars
  }

  // Create snackbar container
  const snackbar = document.createElement("div");
  snackbar.className = "md3-snackbar md3-snackbar--auth-expired";
  snackbar.setAttribute("role", "status");
  snackbar.setAttribute("aria-live", "polite");

  // Create content
  snackbar.innerHTML = `
    <div class="md3-snackbar__surface">
      <div class="md3-snackbar__label">
        Sitzung abgelaufen. Erneut anmelden.
      </div>
      <div class="md3-snackbar__actions">
        <button type="button" class="md3-snackbar__action" data-action="open-login">
          Anmelden
        </button>
        <button type="button" class="md3-snackbar__dismiss" aria-label="Schließen">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
    </div>
  `;

  // Add to DOM
  document.body.appendChild(snackbar);

  // Animate in
  requestAnimationFrame(() => {
    snackbar.classList.add("md3-snackbar--visible");
  });

  // Handle action button (open login)
  const actionButton = snackbar.querySelector('[data-action="open-login"]');
  if (actionButton) {
    actionButton.addEventListener("click", () => {
      // Open login dialog/sheet
      const loginTrigger = document.querySelector('[data-action="open-login"]');
      if (loginTrigger && loginTrigger !== actionButton) {
        loginTrigger.click();
      }

      // Close snackbar
      dismissSnackbar(snackbar);
    });
  }

  // Handle dismiss button
  const dismissButton = snackbar.querySelector(".md3-snackbar__dismiss");
  if (dismissButton) {
    dismissButton.addEventListener("click", () => {
      dismissSnackbar(snackbar);
    });
  }
}

/**
 * Dismiss snackbar with animation
 * @param {HTMLElement} snackbar
 */
function dismissSnackbar(snackbar) {
  snackbar.classList.remove("md3-snackbar--visible");

  // Remove from DOM after animation
  setTimeout(() => {
    snackbar.remove();
  }, 300); // Match CSS transition duration
}
