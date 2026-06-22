function updateExpandedHeight(expandable) {
    const viewport = expandable.querySelector("[data-pm-expandable-viewport]");
    if (!viewport) {
        return;
    }
    viewport.style.setProperty("--pm-expandable-expanded-height", `${viewport.scrollHeight}px`);
}

export function setReadingExpandableState(expandable, expanded) {
    const toggle = expandable.querySelector("[data-pm-expandable-toggle]");
    const label = expandable.querySelector("[data-pm-expandable-toggle-label]");
    if (!toggle || !label) {
        return;
    }

    updateExpandedHeight(expandable);
    expandable.classList.toggle("is-expanded", expanded);
    toggle.setAttribute("aria-expanded", String(expanded));
    label.textContent = expanded ? toggle.dataset.labelHide : toggle.dataset.labelShow;
}

export function initReadingExpandables(root = document) {
    const expandables = [...root.querySelectorAll("[data-pm-expandable]")];
    if (!expandables.length) {
        return;
    }

    for (const expandable of expandables) {
        if (expandable.dataset.pmExpandableReady === "true") {
            updateExpandedHeight(expandable);
            continue;
        }

        const toggle = expandable.querySelector("[data-pm-expandable-toggle]");
        if (!toggle) {
            continue;
        }

        expandable.dataset.pmExpandableReady = "true";
        setReadingExpandableState(expandable, false);
        toggle.addEventListener("click", () => {
            setReadingExpandableState(expandable, toggle.getAttribute("aria-expanded") !== "true");
        });
    }
}

let resizeFrame = null;

export function refreshExpandedReadingLists() {
    if (resizeFrame !== null) {
        cancelAnimationFrame(resizeFrame);
    }
    resizeFrame = requestAnimationFrame(() => {
        for (const expandable of document.querySelectorAll("[data-pm-expandable]")) {
            updateExpandedHeight(expandable);
        }
        resizeFrame = null;
    });
}
