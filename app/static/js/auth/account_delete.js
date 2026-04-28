import { showError, showSuccess, clearAlert } from '/static/js/md3/alert-utils.js';

function loadConfig(templateId) {
  const template = document.getElementById(templateId);
  if (!template) return {};
  try {
    return JSON.parse(template.textContent || '{}');
  } catch (error) {
    console.error(`Failed to parse ${templateId}`, error);
    return {};
  }
}

const accountDeleteConfig = loadConfig('account-delete-config');
const accountDeleteI18n = accountDeleteConfig.i18n || {};

function t(key, fallback) {
  return accountDeleteI18n[key] || fallback;
}

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('del');
  if (!form) return;
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const status = document.getElementById('status');
    clearAlert(status);
    
    try {
      const password = document.getElementById('pw').value;
      const r = await fetch('/auth/account/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password }) });
      const j = await r.json();
      
      if (r.status === 202) {
        showSuccess(status, t('accepted', 'Löschanfrage akzeptiert. Du wirst weitergeleitet...'));
        window.location = '/';
      } else {
        showError(status, j.message || t('deleteError', 'Fehler beim Löschen des Kontos.'));
      }
    } catch (error) {
      console.error('[Account Delete] Error:', error);
      showError(status, t('networkError', 'Ein Netzwerkfehler ist aufgetreten.'));
    }
  });
});
