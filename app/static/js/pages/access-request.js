const formSelector = "[data-access-request-form]";

function resetSubmitButton(button) {
  if (!button) {
    return;
  }
  const label = button.querySelector("[data-access-request-submit-label]");
  if (button.dataset.defaultLabel && label) {
    label.textContent = button.dataset.defaultLabel;
  }
  button.disabled = false;
  button.removeAttribute("aria-busy");
  button.classList.remove("is-pending");
}

function markSubmitting(button) {
  if (!button) {
    return;
  }
  const label = button.querySelector("[data-access-request-submit-label]");
  if (label && !button.dataset.defaultLabel) {
    button.dataset.defaultLabel = label.textContent;
  }
  if (label && button.dataset.pendingLabel) {
    label.textContent = button.dataset.pendingLabel;
  }
  button.disabled = true;
  button.setAttribute("aria-busy", "true");
  button.classList.add("is-pending");
}

function initAccessRequestForm(form) {
  if (!form) {
    return;
  }
  const submitButton = form.querySelector("[data-access-request-submit]");
  form.addEventListener("submit", () => {
    markSubmitting(submitButton);
  });
  window.addEventListener("pageshow", () => {
    resetSubmitButton(submitButton);
  });
}

document.querySelectorAll(formSelector).forEach(initAccessRequestForm);