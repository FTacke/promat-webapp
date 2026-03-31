/**
 * UI Utilities
 * Handles preload guard, page title updates, and scroll state.
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



export function initPageTitleAndScroll() {
  if (window.__pageTitleInit) return;
  window.__pageTitleInit = true;

  const TITLE_TEXT = 'Pronunciation Matters';

  function applyTitle() {
    const t = TITLE_TEXT;
    const el = document.querySelector('[data-page-title-el]');
    if (el) el.textContent = t;
    document.title = t;
  }

  function applyScroll() {
    const thr = 8;
    if (window.scrollY > thr) {
      document.body.setAttribute('data-scrolled', 'true');
    } else {
      document.body.removeAttribute('data-scrolled');
    }
  }

  applyTitle();
  applyScroll();
  window.addEventListener('scroll', applyScroll, { passive: true });

  if (window.htmx) {
    document.body.addEventListener('htmx:afterSwap', function() {
      applyTitle();
      applyScroll();
    });
    document.body.addEventListener('htmx:afterSettle', function() {
      applyTitle();
      applyScroll();
    });
    document.body.addEventListener('htmx:historyRestore', function() {
      applyTitle();
      applyScroll();
    });
  }

  if (window.Turbo) {
    document.addEventListener('turbo:render', function() {
      applyTitle();
      applyScroll();
    });
  }

  window.addEventListener('popstate', function() {
    applyTitle();
    applyScroll();
  });
  
  // Also run on DOMContentLoaded if not already there (though this function is likely called from there)
  if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        applyTitle();
        applyScroll();
      });
  }
}
