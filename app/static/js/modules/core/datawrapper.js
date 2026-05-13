const DATAWRAPPER_FLAG = "__promatDatawrapperResizeInit";

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
  if (!isDatawrapperPayload(event.data)) {
    return;
  }
  updateMatchingIframe(event.source, event.data["datawrapper-height"]);
}

export function initDatawrapperEmbeds() {
  if (window[DATAWRAPPER_FLAG]) {
    return;
  }
  window.addEventListener("message", handleDatawrapperMessage);
  window[DATAWRAPPER_FLAG] = true;
}
