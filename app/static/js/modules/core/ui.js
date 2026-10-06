/**
 * UI Utilities
 * Handles preload guard and scroll state. The document title is rendered by the server per route and is never
 * rewritten on the client.
 */

export function initPreloadGuard() {
  document.body.classList.add('preload');
  requestAnimationFrame(() => {
    document.body.classList.remove('preload');
    document.documentElement.setAttribute('data-anim-ready', '1');
  });
  // Also enable on first user interaction (fallback for slow browsers)
  window.addEventListener('pointerdown', () => {
    document.documentElement.setAttribute('data-anim-ready', '1');
  }, { once: true });
}



export function initScrollIndicator() {
  if (window.__scrollIndicatorInit) return;
  window.__scrollIndicatorInit = true;

  function applyScroll() {
    const thr = 8;
    if (window.scrollY > thr) {
      document.body.setAttribute('data-scrolled', 'true');
    } else {
      document.body.removeAttribute('data-scrolled');
    }
  }

  applyScroll();
  window.addEventListener('scroll', applyScroll, { passive: true });

  if (window.htmx) {
    document.body.addEventListener('htmx:afterSwap', applyScroll);
    document.body.addEventListener('htmx:afterSettle', applyScroll);
    document.body.addEventListener('htmx:historyRestore', applyScroll);
  }

  if (window.Turbo) {
    document.addEventListener('turbo:render', applyScroll);
  }

  window.addEventListener('popstate', applyScroll);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyScroll);
  }
}
