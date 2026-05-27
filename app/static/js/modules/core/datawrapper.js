const DATAWRAPPER_FLAG = "__promatDatawrapperResizeInit";
const DATAWRAPPER_ORIGIN = "https://datawrapper.dwcdn.net";
const DATAWRAPPER_THEME_OBSERVER_FLAG = "__promatDatawrapperThemeObserver";

export function isAllowedDatawrapperOrigin(origin) {
  return origin === DATAWRAPPER_ORIGIN;
}

export function getEffectiveDatawrapperDarkMode(root = document.documentElement) {
  const theme = root?.dataset?.theme || "auto";
  if (theme === "dark") {
    return true;
  }
  if (theme === "light") {
    return false;
  }
  return root?.dataset?.systemDark === "true";
}

export function withDatawrapperDarkFlag(src, darkMode) {
  try {
    const url = new URL(src);
    if (!isAllowedDatawrapperOrigin(url.origin)) {
      return src;
    }
    url.searchParams.set("dark", darkMode ? "true" : "false");
    return url.toString();
  } catch {
    return src;
  }
}

function syncDatawrapperThemeFlags() {
  const darkMode = getEffectiveDatawrapperDarkMode();
  const iframes = document.querySelectorAll('iframe[data-provider="datawrapper"]');
  for (const iframe of iframes) {
    const nextDark = darkMode ? "true" : "false";
    if (iframe.dataset.promatDatawrapperDark === nextDark) {
      continue;
    }
    const nextSrc = withDatawrapperDarkFlag(iframe.getAttribute("src") || "", darkMode);
    iframe.dataset.promatDatawrapperDark = nextDark;
    if (nextSrc && nextSrc !== iframe.getAttribute("src")) {
      iframe.setAttribute("src", nextSrc);
    }
  }
}

function isDatawrapperPayload(value) {
  return Boolean(value) && typeof value === "object" && typeof value["datawrapper-height"] === "object";
}

function updateMatchingIframe(sourceWindow, heights) {
  const iframes = document.querySelectorAll('iframe[data-provider="datawrapper"]');
  if (!iframes.length) {
    return;
  }

  for (const iframe of iframes) {
    if (iframe.contentWindow !== sourceWindow) {
      continue;
    }
    for (const nextHeight of Object.values(heights)) {
      const parsedHeight = Number(nextHeight);
      if (Number.isFinite(parsedHeight) && parsedHeight > 0) {
        iframe.style.height = `${parsedHeight}px`;
        return;
      }
    }
  }
}

function handleDatawrapperMessage(event) {
  if (!isAllowedDatawrapperOrigin(event.origin)) {
    return;
  }
  if (!isDatawrapperPayload(event.data)) {
    return;
  }
  updateMatchingIframe(event.source, event.data["datawrapper-height"]);
}

export function initDatawrapperEmbeds() {
  syncDatawrapperThemeFlags();

  if (window[DATAWRAPPER_FLAG]) {
    return;
  }
  window.addEventListener("message", handleDatawrapperMessage);
  window[DATAWRAPPER_FLAG] = true;

  if (!window[DATAWRAPPER_THEME_OBSERVER_FLAG] && typeof MutationObserver !== "undefined") {
    const observer = new MutationObserver(syncDatawrapperThemeFlags);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme", "data-system-dark"],
    });
    window[DATAWRAPPER_THEME_OBSERVER_FLAG] = observer;
  }
}
