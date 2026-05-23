const PLAYER_LINK_SELECTOR = 'a[href*="/player/"][href*="source=speakers"]';
const warmedHrefs = new Set();

function warmPlayerRoute(href) {
  if (!href || warmedHrefs.has(href)) {
    return;
  }

  warmedHrefs.add(href);
  void fetch(href, {
    credentials: 'same-origin',
    headers: {
      'X-Promat-Player-Prewarm': '1',
    },
  }).catch(() => {
    warmedHrefs.delete(href);
  });
}

function warmLinkTarget(target) {
  if (!(target instanceof Element)) {
    return;
  }
  const link = target.closest(PLAYER_LINK_SELECTOR);
  if (!(link instanceof HTMLAnchorElement)) {
    return;
  }
  warmPlayerRoute(link.href);
}

document.addEventListener('pointerenter', (event) => {
  warmLinkTarget(event.target);
}, { capture: true });

document.addEventListener('focusin', (event) => {
  warmLinkTarget(event.target);
});

document.addEventListener('touchstart', (event) => {
  warmLinkTarget(event.target);
}, { capture: true, passive: true });