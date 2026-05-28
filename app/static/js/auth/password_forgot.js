document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('forgot');
  const configElement = document.getElementById('password-forgot-config');
  if (!form || !configElement || !window.fetch) {
    return;
  }

  let config = {};
  try {
    const raw = (configElement.content && configElement.content.textContent) || configElement.textContent || '{}';
    config = JSON.parse(raw);
  } catch (error) {
    console.error('Failed to parse password reset config.', error);
  }

  const text = config.i18n || {};
  const submitButton = form.querySelector('[data-password-forgot-submit]');
  const label = submitButton ? submitButton.querySelector('.pm-action-button__label') : null;
  const initialLabel = label ? label.textContent : '';

  function t(key, fallback) {
    return text[key] || fallback;
  }

  function setMessage(message, type) {
    let messageElement = form.parentElement ? form.parentElement.querySelector('[data-password-forgot-status]') : null;
    if (!messageElement) {
      messageElement = document.createElement('div');
      messageElement.className = 'pm-auth-message';
      messageElement.setAttribute('role', 'status');
      messageElement.setAttribute('aria-live', 'polite');
      messageElement.dataset.passwordForgotStatus = 'true';
      messageElement.innerHTML = `
        <span class="pm-auth-message__icon material-symbols-rounded" aria-hidden="true">info</span>
        <div class="pm-auth-message__body">
          <p class="pm-auth-message__eyebrow">${t('notice', 'Notice')}</p>
          <p class="pm-auth-message__text"></p>
        </div>
      `;
      form.insertAdjacentElement('beforebegin', messageElement);
    }
    messageElement.classList.toggle('is-error', type === 'error');
    messageElement.classList.toggle('is-success', type !== 'error');
    const textElement = messageElement.querySelector('.pm-auth-message__text');
    if (textElement) {
      textElement.textContent = message;
    }
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const endpoint = form.dataset.passwordResetRequestEndpoint || form.action;
    const formData = new FormData(form);
    const email = (formData.get('email') || '').toString().trim();
    if (!email) {
      setMessage(t('emailRequired', 'Please enter an email address.'), 'error');
      return;
    }

    if (submitButton) {
      submitButton.disabled = true;
    }
    if (label) {
      label.textContent = t('sending', 'Sending ...');
    }

    fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        email,
        ui_lang: config.uiLang || formData.get('ui_lang') || 'de',
      }),
    })
      .then((response) => response.json().then((payload) => ({ ok: response.ok, payload })))
      .then(({ ok, payload }) => {
        if (!ok || !payload.ok) {
          throw new Error(payload.message || t('networkError', 'The request could not be completed.'));
        }
        setMessage(payload.message || t('success', 'If an account exists for this address, a new link has been prepared.'), 'success');
        form.reset();
      })
      .catch((error) => {
        setMessage(error.message || t('networkError', 'The request could not be completed.'), 'error');
      })
      .finally(() => {
        if (submitButton) {
          submitButton.disabled = false;
        }
        if (label) {
          label.textContent = initialLabel || t('submit', 'Request reset link');
        }
      });
  });
});
