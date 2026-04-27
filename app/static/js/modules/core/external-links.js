const EXTERNAL_HTTP_PROTOCOLS = new Set(["http:", "https:"]);

function isExternalHttpLink(anchor) {
  const href = anchor.getAttribute("href");
  if (!href) {
    return false;
  }

  let url;
  try {
    url = new URL(href, window.location.href);
  } catch {
    return false;
  }

  if (!EXTERNAL_HTTP_PROTOCOLS.has(url.protocol)) {
    return false;
  }

  return url.origin !== window.location.origin;
}

function decorateExternalLink(anchor) {
  if (!isExternalHttpLink(anchor)) {
    return;
  }

  anchor.setAttribute("target", "_blank");

  const relTokens = new Set(
    (anchor.getAttribute("rel") || "")
      .split(/\s+/)
      .map((token) => token.trim())
      .filter(Boolean),
  );
  relTokens.add("noopener");
  relTokens.add("noreferrer");
  anchor.setAttribute("rel", Array.from(relTokens).join(" "));
}

function decorateNode(node) {
  if (!(node instanceof Element)) {
    return;
  }

  if (node.matches("a[href]")) {
    decorateExternalLink(node);
  }

  node.querySelectorAll("a[href]").forEach(decorateExternalLink);
}

export function initExternalHttpLinks() {
  decorateNode(document.documentElement);

  if (!document.body) {
    return;
  }

  const observer = new MutationObserver((records) => {
    for (const record of records) {
      if (record.type === "attributes" && record.target instanceof HTMLAnchorElement) {
        decorateExternalLink(record.target);
        continue;
      }

      record.addedNodes.forEach(decorateNode);
    }
  });

  observer.observe(document.body, {
    subtree: true,
    childList: true,
    attributes: true,
    attributeFilter: ["href"],
  });
}