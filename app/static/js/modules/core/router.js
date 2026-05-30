/**
 * Page Router
 * Dynamically initialize page-specific modules based on data-page attribute.
 */

const pageInits = {
  // Register page initializers here, keyed by the data-page attribute value.
  // Example:
  //   mypage: async () => { const mod = await import('../../pages/mypage.js'); mod?.init?.(); }
};

export function initPageRouter() {
  const page = document.body.dataset.page;
  if (!page) return;
  
  const init = pageInits[page];
  if (init) {
    init();
  }
}
