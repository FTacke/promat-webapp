// Commit a <select> choice only when the user actually decided.
//
// A native select fires `change` for every Arrow key press while it is closed (Chrome, Edge), so a handler that
// navigates or reloads on `change` fires while a keyboard user is merely browsing the options (WCAG 3.2.2 On Input).
// Pointer and screen-reader selections commit immediately; keyboard browsing commits on Enter or when the select
// loses focus.

const BROWSING_KEYS = new Set(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "PageUp", "PageDown", "Home", "End"]);

export function bindSelectCommit(select, onCommit) {
  let committedValue = select.value;
  let keyboardBrowsing = false;
  let enterPressed = false;

  const commit = () => {
    keyboardBrowsing = false;
    if (select.value === committedValue) {
      return;
    }
    committedValue = select.value;
    onCommit(select.value);
  };

  select.addEventListener("pointerdown", () => {
    keyboardBrowsing = false;
  });
  select.addEventListener("keydown", (event) => {
    if (BROWSING_KEYS.has(event.key)) {
      keyboardBrowsing = true;
    } else if (event.key === "Enter") {
      enterPressed = true;
      window.setTimeout(() => {
        enterPressed = false;
      }, 0);
      if (keyboardBrowsing) {
        commit();
      }
    }
  });
  select.addEventListener("change", () => {
    if (keyboardBrowsing && !enterPressed) {
      return;
    }
    commit();
  });
  select.addEventListener("blur", () => {
    if (keyboardBrowsing) {
      commit();
    }
  });
  // Lets the owner re-sync after it re-rendered the options or refused a change.
  return {
    reset(value = select.value) {
      committedValue = value;
      keyboardBrowsing = false;
    },
  };
}
