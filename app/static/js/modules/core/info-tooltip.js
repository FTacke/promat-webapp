export function initInfoTooltips() {
  document.addEventListener("click", (event) => {
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
    const openTips = document.querySelectorAll("details.pm-info-tip[open]");
    openTips.forEach((tip) => {
      tip.removeAttribute("open");
      const trigger = tip.querySelector(".pm-info-tip__trigger");
      if (trigger) trigger.focus();
    });
  });
}
