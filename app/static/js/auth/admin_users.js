document.addEventListener('DOMContentLoaded', () => {
  function readConfig() {
    const element = document.getElementById('admin-users-config');
    if (!element) {
      return {};
    }
    try {
      const raw = (element.content && element.content.textContent) || element.innerHTML || '{}';
      return JSON.parse(raw);
    } catch (error) {
      console.error('Failed to parse admin users config.', error);
      return {};
    }
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrf_access_token=([^;]+)/);
    return match ? match[1] : '';
  }

  function buildAdminUrl(path, params) {
    const url = new URL(path, window.location.origin);
    if (uiLang) {
      url.searchParams.set('ui_lang', uiLang);
    }
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          url.searchParams.set(key, value);
        }
      });
    }
    return `${url.pathname}${url.search}`;
  }

  const config = readConfig();
  const text = config.i18n || {};
  const uiLang = config.uiLang || 'de';
  const locale = uiLang === 'en' ? 'en-GB' : 'de-DE';
  const roleLabels = {
    user: text.roleUser || 'User',
    admin: text.roleAdmin || 'Admin',
  };
  const roleIcons = {
    user: 'person',
    admin: 'verified_user',
  };
  const statusLabels = {
    active: text.statusActive || 'Active',
    invited: text.statusInvited || 'Invited',
    deactivated: text.statusDeactivated || 'Deactivated',
    expired: text.statusExpired || 'Expired',
  };
  const statusIcons = {
    active: 'check_circle',
    invited: 'mail',
    deactivated: 'block',
    expired: 'schedule',
  };

  const listBody = document.getElementById('list-body');
  const refreshBtn = document.getElementById('refresh');
  const searchInput = document.getElementById('admin-search');
  const filterInactiveBtn = document.getElementById('filter-inactive');
  const sortSelect = document.getElementById('admin-sort');

  const createBtn = document.getElementById('create');
  const createDialog = document.getElementById('create-user-dialog');
  const createForm = document.getElementById('create-user-form');
  const cancelCreateBtn = document.getElementById('cancel-create');

  const inviteDialog = document.getElementById('invite-dialog');
  const inviteLinkCode = document.getElementById('invite-link');
  const inviteMailSubject = document.getElementById('invite-mail-subject');
  const inviteMailBody = document.getElementById('invite-mail-body');
  const inviteMeta = document.getElementById('invite-meta');
  const copyInviteBtn = document.getElementById('copy-invite');
  const copyInviteMailBtn = document.getElementById('copy-invite-mail');
  const closeInviteBtn = document.getElementById('close-invite');
  const inviteCopyStatus = document.getElementById('invite-copy-status');

  const editDialog = document.getElementById('user-edit-dialog');
  const saveEditBtn = document.getElementById('save-edit');
  const cancelEditBtn = document.getElementById('cancel-edit');
  const editUserId = document.getElementById('edit-user-id');
  const editFirstName = document.getElementById('edit-first-name');
  const editLastName = document.getElementById('edit-last-name');
  const editEmail = document.getElementById('edit-email');
  const editEmailError = document.getElementById('edit-email-error');
  const editAccessExpiresOn = document.getElementById('edit-access-expires-on');
  const editRole = document.getElementById('edit-role');
  const editIsActive = document.getElementById('edit-is-active');
  const editResetPasswordBtn = document.getElementById('edit-reset-password');
  const editError = document.getElementById('user-edit-error');

  let includeInactive = false;
  let searchDebounce = null;
  let toastTimer = null;

  function t(key, fallback = '') {
    return text[key] || fallback;
  }

  function escapeHtml(value) {
    const node = document.createElement('div');
    node.textContent = value || '';
    return node.innerHTML;
  }

  function formatDateTime(value) {
    if (!value) {
      return '–';
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString(locale);
  }

  function formatDate(value) {
    if (!value) {
      return '–';
    }
    const date = new Date(`${value}T00:00:00`);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleDateString(locale);
  }

  function setDialogOpen(dialog, open) {
    if (!dialog) {
      return;
    }
    if (open) {
      try {
        dialog.showModal();
      } catch (error) {
        dialog.setAttribute('open', 'true');
      }
      return;
    }
    try {
      dialog.close();
    } catch (error) {
      dialog.removeAttribute('open');
    }
  }

  function dismissToast() {
    const existing = document.querySelector('.pm-admin-toast');
    if (existing) {
      existing.remove();
    }
    if (toastTimer) {
      window.clearTimeout(toastTimer);
      toastTimer = null;
    }
  }

  function getToastHost() {
    const openDialogs = Array.from(document.querySelectorAll('dialog[open]'));
    return openDialogs.at(-1) || document.body;
  }

  function showToast(message, type = 'success') {
    const globalSnackbar = window.showSnackbar || window.MD3Snackbar?.showSnackbar;
    if (globalSnackbar) {
      globalSnackbar(message, type);
      return;
    }
    dismissToast();
    const toast = document.createElement('div');
    toast.className = `pm-admin-toast${type === 'error' ? ' pm-admin-toast--error' : ''}`;
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.innerHTML = `
      <p class="pm-admin-toast__eyebrow">${escapeHtml(t('notice', 'Notice'))}</p>
      <p class="pm-admin-toast__text">${escapeHtml(message)}</p>
      <button type="button" class="pm-research-inline-action pm-research-inline-action--secondary pm-research-inline-action--compact pm-admin-toast__action">${escapeHtml(t('close', 'Close'))}</button>
    `;
    getToastHost().appendChild(toast);
    const action = toast.querySelector('.pm-admin-toast__action');
    if (action) {
      action.addEventListener('click', dismissToast);
    }
    toastTimer = window.setTimeout(dismissToast, 4000);
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email || '');
  }

  function validateNames(firstName, lastName) {
    return Boolean((firstName || '').trim() && (lastName || '').trim());
  }

  function renderRoleBadge(role) {
    return `
      <span class="pm-admin-badge pm-admin-badge--role-${escapeHtml(role)}">
        <span class="material-symbols-rounded pm-admin-badge__icon" aria-hidden="true">${roleIcons[role] || 'person'}</span>
        <span>${escapeHtml(roleLabels[role] || role)}</span>
      </span>
    `;
  }

  function renderStatusBadge(statusCode) {
    return `
      <span class="pm-admin-badge pm-admin-badge--status-${escapeHtml(statusCode)}">
        <span class="material-symbols-rounded pm-admin-badge__icon" aria-hidden="true">${statusIcons[statusCode] || 'info'}</span>
        <span>${escapeHtml(statusLabels[statusCode] || statusCode)}</span>
      </span>
    `;
  }

  function renderRow(user) {
    const row = document.createElement('tr');
    const createdBy = user.created_by_name || (user.created_by_is_system ? t('createdBySystem', 'System') : '–');
    row.dataset.userId = user.id;
    row.innerHTML = `
      <td><span class="pm-admin-table__primary">${escapeHtml(user.last_name || '–')}</span></td>
      <td><span class="pm-admin-table__primary">${escapeHtml(user.first_name || '–')}</span></td>
      <td><div class="pm-admin-table__email"><span class="pm-admin-table__primary">${escapeHtml(user.email || '–')}</span></div></td>
      <td>${renderRoleBadge(user.role)}</td>
      <td>${renderStatusBadge(user.status_code)}</td>
      <td class="pm-admin-table__desktop"><span class="pm-admin-table__meta">${escapeHtml(formatDate(user.access_expires_on))}</span></td>
      <td class="pm-admin-table__desktop"><span class="pm-admin-table__meta">${escapeHtml(formatDateTime(user.created_at))}</span></td>
      <td class="pm-admin-table__desktop"><span class="pm-admin-table__meta">${escapeHtml(createdBy)}</span></td>
      <td>
        <div class="pm-admin-table__actions">
          <button class="pm-research-inline-action pm-research-inline-action--secondary pm-research-inline-action--compact pm-admin-table__action edit-user-btn" type="button" data-id="${escapeHtml(user.id)}" title="${escapeHtml(t('editTitle', 'Edit user'))}" aria-label="${escapeHtml(t('editTitle', 'Edit user'))}">
            <span class="material-symbols-rounded" aria-hidden="true">edit</span>
            <span>${escapeHtml(t('editTitle', 'Edit user'))}</span>
          </button>
        </div>
      </td>
    `;
    return row;
  }

  function setLoadingState() {
    if (!listBody) {
      return;
    }
    listBody.innerHTML = `<tr><td colspan="9" class="pm-admin-table__empty">${escapeHtml(t('loading', 'Loading...'))}</td></tr>`;
  }

  function showEditError(message) {
    if (!editError) {
      showToast(message, 'error');
      return;
    }
    const messageElement = editError.querySelector('.pm-admin-alert__text');
    if (messageElement) {
      messageElement.textContent = message;
    }
    editError.hidden = false;
  }

  function clearEditError() {
    if (editError) {
      editError.hidden = true;
    }
    if (editEmailError) {
      editEmailError.textContent = '';
    }
  }

  function syncExpiryFieldForRole(roleField, expiryField) {
    if (!roleField || !expiryField) {
      return;
    }
    const isAdmin = roleField.value === 'admin';
    expiryField.disabled = isAdmin;
    if (isAdmin) {
      expiryField.value = '';
    }
  }

  function populateInviteDialog(payload) {
    if (inviteLinkCode) {
      inviteLinkCode.textContent = payload.inviteLink || '';
    }
    if (inviteMailSubject) {
      inviteMailSubject.value = payload.inviteMailSubject || '';
    }
    if (inviteMailBody) {
      inviteMailBody.value = payload.inviteMailBody || '';
    }
    if (inviteMeta) {
      inviteMeta.textContent = payload.inviteExpiresAt ? `${t('expiresPrefix', 'Valid until')}: ${formatDateTime(payload.inviteExpiresAt)}` : '';
    }
  }

  function copyText(value, successMessage) {
    if (!navigator.clipboard) {
      showToast(t('copyFailed', 'Copy failed.'), 'error');
      return;
    }
    navigator.clipboard.writeText(value)
      .then(() => {
        if (inviteCopyStatus) {
          inviteCopyStatus.textContent = successMessage;
        }
        showToast(successMessage, 'success');
        window.setTimeout(() => {
          if (inviteCopyStatus) {
            inviteCopyStatus.textContent = '';
          }
        }, 1500);
      })
      .catch((error) => {
        console.error(error);
        showToast(t('copyFailed', 'Copy failed.'), 'error');
      });
  }

  function openEditDialog(userId) {
    if (!userId) {
      return;
    }
    clearEditError();
    fetch(buildAdminUrl(`/admin/users/${encodeURIComponent(userId)}`), {
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(t('loadError', 'Could not load users.'));
        }
        return response.json();
      })
      .then((user) => {
        if (editUserId) {
          editUserId.value = user.id;
        }
        if (editFirstName) {
          editFirstName.value = user.first_name || '';
        }
        if (editLastName) {
          editLastName.value = user.last_name || '';
        }
        if (editEmail) {
          editEmail.value = user.email || '';
        }
        if (editAccessExpiresOn) {
          editAccessExpiresOn.value = user.access_expires_on || '';
        }
        if (editRole) {
          editRole.value = user.role;
        }
        syncExpiryFieldForRole(editRole, editAccessExpiresOn);
        if (editIsActive) {
          editIsActive.checked = Boolean(user.is_active);
        }
        setDialogOpen(editDialog, true);
      })
      .catch((error) => {
        console.error(error);
        showToast(error.message || t('loadError', 'Could not load users.'), 'error');
      });
  }

  function bindEditButtons() {
    document.querySelectorAll('.edit-user-btn').forEach((button) => {
      button.addEventListener('click', () => openEditDialog(button.dataset.id));
    });
  }

  function reload() {
    if (!listBody) {
      return;
    }
    setLoadingState();
    const params = new URLSearchParams();
    if (includeInactive) {
      params.set('include_inactive', '1');
    }
    const query = searchInput ? searchInput.value.trim() : '';
    if (query) {
      params.set('q', query);
    }
    if (sortSelect && sortSelect.value) {
      params.set('sort', sortSelect.value);
    }

    fetch(buildAdminUrl('/admin/users', Object.fromEntries(params.entries())), {
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(t('loadError', 'Could not load users.'));
        }
        return response.json();
      })
      .then((payload) => {
        listBody.innerHTML = '';
        if (!payload.items || payload.items.length === 0) {
          listBody.innerHTML = `<tr><td colspan="9" class="pm-admin-table__empty">${escapeHtml(t('noUsers', 'No users found.'))}</td></tr>`;
          return;
        }
        payload.items.forEach((user) => listBody.appendChild(renderRow(user)));
        bindEditButtons();
      })
      .catch((error) => {
        console.error(error);
        listBody.innerHTML = `<tr><td colspan="6" class="pm-admin-table__empty">${escapeHtml(error.message || t('loadError', 'Could not load users.'))}</td></tr>`;
      });
  }

  function saveEdit() {
    if (!editUserId || !editUserId.value) {
      return;
    }
    clearEditError();
    const firstName = editFirstName ? editFirstName.value.trim() : '';
    const lastName = editLastName ? editLastName.value.trim() : '';
    const email = editEmail ? editEmail.value.trim() : '';
    if (!validateNames(firstName, lastName)) {
      showEditError(t('requiredNames', 'First name and last name are required.'));
      return;
    }
    if (!validateEmail(email)) {
      if (editEmailError) {
        editEmailError.textContent = t('invalidEmail', 'Please enter a valid email address.');
      }
      showEditError(t('invalidEmail', 'Please enter a valid email address.'));
      return;
    }

    const originalLabel = saveEditBtn ? saveEditBtn.textContent : '';
    if (saveEditBtn) {
      saveEditBtn.disabled = true;
      saveEditBtn.textContent = t('saving', 'Saving...');
    }

    fetch(buildAdminUrl(`/admin/users/${encodeURIComponent(editUserId.value)}`), {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRF-TOKEN': getCsrfToken(),
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email,
        role: editRole ? editRole.value : 'user',
        is_active: editIsActive ? editIsActive.checked : true,
        access_expires_on: editAccessExpiresOn ? editAccessExpiresOn.value : '',
      }),
    })
      .then((response) => response.json())
      .then((payload) => {
        if (!payload.ok) {
          throw new Error(payload.error || t('networkError', 'Network error. Please try again.'));
        }
        setDialogOpen(editDialog, false);
        reload();
        showToast(t('updated', 'User updated.'), 'success');
      })
      .catch((error) => {
        console.error(error);
        showEditError(error.message || t('networkError', 'Network error. Please try again.'));
      })
      .finally(() => {
        if (saveEditBtn) {
          saveEditBtn.disabled = false;
          saveEditBtn.textContent = originalLabel || t('save', 'Save');
        }
      });
  }

  function prepareReset() {
    if (!editUserId || !editUserId.value) {
      return;
    }
    const originalLabel = editResetPasswordBtn ? editResetPasswordBtn.textContent : '';
    if (editResetPasswordBtn) {
      editResetPasswordBtn.disabled = true;
      editResetPasswordBtn.textContent = t('sending', 'Preparing...');
    }

    fetch(buildAdminUrl(`/admin/users/${encodeURIComponent(editUserId.value)}/reset-password`), {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'X-CSRF-TOKEN': getCsrfToken(),
      },
      credentials: 'same-origin',
    })
      .then((response) => response.json())
      .then((payload) => {
        if (!payload.ok) {
          throw new Error(payload.error || t('networkError', 'Network error. Please try again.'));
        }
        populateInviteDialog(payload);
        setDialogOpen(editDialog, false);
        setDialogOpen(inviteDialog, true);
        showToast(t('resetPrepared', 'Password link prepared.'), 'success');
      })
      .catch((error) => {
        console.error(error);
        showToast(error.message || t('networkError', 'Network error. Please try again.'), 'error');
      })
      .finally(() => {
        if (editResetPasswordBtn) {
          editResetPasswordBtn.disabled = false;
          editResetPasswordBtn.textContent = originalLabel || t('resetPassword', 'Prepare new link');
        }
      });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', reload);
  }
  if (filterInactiveBtn) {
    filterInactiveBtn.addEventListener('click', () => {
      includeInactive = !includeInactive;
      filterInactiveBtn.classList.toggle('is-active', includeInactive);
      filterInactiveBtn.setAttribute('aria-pressed', includeInactive ? 'true' : 'false');
      const icon = filterInactiveBtn.querySelector('.material-symbols-rounded');
      if (icon) {
        icon.textContent = includeInactive ? 'visibility' : 'visibility_off';
      }
      reload();
    });
  }
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      window.clearTimeout(searchDebounce);
      searchDebounce = window.setTimeout(reload, 250);
    });
  }
  if (sortSelect) {
    sortSelect.addEventListener('change', reload);
  }
  if (createBtn) {
    createBtn.addEventListener('click', () => {
      if (createForm) {
        createForm.reset();
      }
      syncExpiryFieldForRole(document.getElementById('new-role'), document.getElementById('new-access-expires-on'));
      setDialogOpen(createDialog, true);
    });
  }
  if (cancelCreateBtn) {
    cancelCreateBtn.addEventListener('click', () => setDialogOpen(createDialog, false));
  }
  if (createForm) {
    createForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(createForm);
      const payload = Object.fromEntries(formData.entries());
      if (!validateNames(payload.first_name, payload.last_name)) {
        showToast(t('requiredNames', 'First name and last name are required.'), 'error');
        return;
      }
      if (!validateEmail((payload.email || '').trim())) {
        showToast(t('invalidEmail', 'Please enter a valid email address.'), 'error');
        return;
      }
      fetch(buildAdminUrl('/admin/users'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          'X-CSRF-TOKEN': getCsrfToken(),
        },
        credentials: 'same-origin',
        body: JSON.stringify(payload),
      })
        .then((response) => response.json())
        .then((payloadResponse) => {
          if (!payloadResponse.ok) {
            throw new Error(payloadResponse.error || t('networkError', 'Network error. Please try again.'));
          }
          setDialogOpen(createDialog, false);
          populateInviteDialog(payloadResponse);
          setDialogOpen(inviteDialog, true);
          reload();
          showToast(t('created', 'User created.'), 'success');
        })
        .catch((error) => {
          console.error(error);
          showToast(error.message || t('networkError', 'Network error. Please try again.'), 'error');
        });
    });
  }
  if (copyInviteBtn) {
    copyInviteBtn.addEventListener('click', () => copyText(inviteLinkCode ? inviteLinkCode.textContent || '' : '', t('copiedLink', 'Link copied.')));
  }
  if (copyInviteMailBtn) {
    copyInviteMailBtn.addEventListener('click', () => {
      const mailText = `${inviteMailSubject ? inviteMailSubject.value : ''}\n\n${inviteMailBody ? inviteMailBody.value : ''}`.trim();
      copyText(mailText, t('copiedMail', 'Email copied.'));
    });
  }
  if (closeInviteBtn) {
    closeInviteBtn.addEventListener('click', () => setDialogOpen(inviteDialog, false));
  }
  if (cancelEditBtn) {
    cancelEditBtn.addEventListener('click', () => setDialogOpen(editDialog, false));
  }
  if (saveEditBtn) {
    saveEditBtn.addEventListener('click', saveEdit);
  }
  if (editRole) {
    editRole.addEventListener('change', () => syncExpiryFieldForRole(editRole, editAccessExpiresOn));
  }
  const createRole = document.getElementById('new-role');
  const createExpiry = document.getElementById('new-access-expires-on');
  if (createRole) {
    createRole.addEventListener('change', () => syncExpiryFieldForRole(createRole, createExpiry));
    syncExpiryFieldForRole(createRole, createExpiry);
  }
  if (editResetPasswordBtn) {
    editResetPasswordBtn.addEventListener('click', prepareReset);
  }

  reload();
});
