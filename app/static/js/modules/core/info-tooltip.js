const INLINE_TIP_SELECTOR = ".pm-info-tip--inline";

function dismissVisibleInlineTips() {
  // Escape hides a tooltip that is only shown by hover or focus until the pointer or focus leaves it.
  document.querySelectorAll(INLINE_TIP_SELECTOR).forEach((tip) => {
    if (tip.matches(":hover") || tip.matches(":focus-within") || tip.classList.contains("is-open")) {
      tip.classList.add("is-dismissed");
    }
  });
}

function closeInlineTips(except) {
  document.querySelectorAll(`${INLINE_TIP_SELECTOR}.is-open`).forEach((tip) => {
    if (tip === except) return;
    tip.classList.remove("is-open");
    const trigger = tip.querySelector(".pm-info-tip__trigger");
    if (trigger) trigger.setAttribute("aria-expanded", "false");
  });
}

export function initInfoTooltips() {
  const clearDismissed = (event) => {
    const tip = event.target.closest ? event.target.closest(INLINE_TIP_SELECTOR) : null;
    if (tip && !(event.relatedTarget && tip.contains(event.relatedTarget))) tip.classList.remove("is-dismissed");
  };
  document.addEventListener("mouseout", clearDismissed);
  document.addEventListener("focusout", clearDismissed);
  document.addEventListener("click", (event) => {
    const inlineTrigger = event.target.closest(`${INLINE_TIP_SELECTOR} .pm-info-tip__trigger`);
    if (inlineTrigger) {
      // Click or tap pins the ISO code open (touch has no hover); a second click closes it again.
      const inlineTip = inlineTrigger.closest(INLINE_TIP_SELECTOR);
      const willOpen = !inlineTip.classList.contains("is-open");
      closeInlineTips(inlineTip);
      inlineTip.classList.toggle("is-open", willOpen);
      inlineTrigger.setAttribute("aria-expanded", willOpen ? "true" : "false");
      return;
    }
    closeInlineTips(null);

    const trigger = event.target.closest(".pm-info-tip__trigger");

    if (trigger) {
      const thisTip = trigger.closest("details.pm-info-tip");
      // Close all other open tips when opening a new one
      document.querySelectorAll("details.pm-info-tip[open]").forEach((tip) => {
        if (tip !== thisTip) {
          tip.removeAttribute("open");
        }
      });
      return;
    }

    // Close any open tip when clicking outside
    document.querySelectorAll("details.pm-info-tip[open]").forEach((tip) => {
      if (!tip.contains(event.target)) {
        tip.removeAttribute("open");
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    dismissVisibleInlineTips();
    closeInlineTips(null);
    const openTips = document.querySelectorAll("details.pm-info-tip[open]");
    openTips.forEach((tip) => {
      tip.removeAttribute("open");
      const trigger = tip.querySelector(".pm-info-tip__trigger");
      if (trigger) trigger.focus();
    });
  });
}
