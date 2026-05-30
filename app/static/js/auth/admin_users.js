document.addEventListener('DOMContentLoaded', () => {
  function readConfig() {
    const element = document.getElementById('admin-users-config');
    if (!element) {
      return {};
    }
    try {
      const raw = (element.content && element.content.textContent) || element.textContent || '{}';
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

  // Role labels: group accounts get their own type label
  const typeLabelForUser = (user) => {
    if (user.account_kind === 'group') {
      return text.roleGroup || 'Gruppe';
    }
    return user.role === 'admin' ? (text.roleAdmin || 'Admin') : (text.roleUser || 'User');
  };
  const typeIconForUser = (user) => {
    if (user.account_kind === 'group') return 'group';
    return user.role === 'admin' ? 'verified_user' : 'person';
  };
  const typeCssForUser = (user) => {
    if (user.account_kind === 'group') return 'group';
    return user.role === 'admin' ? 'admin' : 'user';
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
  const tableWrap = document.querySelector('.pm-admin-table-wrap');
  const refreshBtn = document.getElementById('refresh');
  const searchInput = document.getElementById('admin-search');
  const filterInactiveBtn = document.getElementById('filter-inactive');
  const sortSelect = document.getElementById('admin-sort');

  // Personal account creation
  const createBtn = document.getElementById('create');
  const createDialog = document.getElementById('create-user-dialog');
  const createForm = document.getElementById('create-user-form');
  const cancelCreateBtn = document.getElementById('cancel-create');

  // Group account creation
  const createGroupBtn = document.getElementById('create-group');
  const createGroupDialog = document.getElementById('create-group-dialog');
  const createGroupForm = document.getElementById('create-group-form');
  const cancelCreateGroupBtn = document.getElementById('cancel-create-group');
  const submitCreateGroupBtn = document.getElementById('submit-create-group');
  const createGroupError = document.getElementById('create-group-error');
  const groupResponsibleAdminSelect = document.getElementById('new-group-responsible-admin');

  // Invite dialog (personal accounts)
  const inviteDialog = document.getElementById('invite-dialog');
  const inviteTitle = document.getElementById('invite-title');
  const inviteIntro = document.getElementById('invite-intro');
  const inviteLinkCode = document.getElementById('invite-link');
  const inviteMailSubject = document.getElementById('invite-mail-subject');
  const inviteMailBody = document.getElementById('invite-mail-body');
  const inviteMeta = document.getElementById('invite-meta');
  const copyInviteBtn = document.getElementById('copy-invite');
  const sendInviteMailBtn = document.getElementById('send-invite-mail');
  const copyInviteMailBtn = document.getElementById('copy-invite-mail');
  const closeInviteBtn = document.getElementById('close-invite');
  const inviteSendStatus = document.getElementById('invite-send-status');
  const inviteCopyStatus = document.getElementById('invite-copy-status');

  // Personal account edit dialog
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
  const editMailLanguage = document.getElementById('edit-mail-language');
  const editSendInviteBtn = document.getElementById('edit-send-invite');
  const editResetPasswordBtn = document.getElementById('edit-reset-password');
  const editError = document.getElementById('user-edit-error');

  // Group account edit dialog
  const groupEditDialog = document.getElementById('group-edit-dialog');
  const saveGroupEditBtn = document.getElementById('save-group-edit');
  const cancelGroupEditBtn = document.getElementById('cancel-group-edit');
  const groupEditUserId = document.getElementById('group-edit-user-id');
  const groupEditDisplayName = document.getElementById('group-edit-display-name');
  const groupEditResponsibleAdmin = document.getElementById('group-edit-responsible-admin');
  const groupEditAccessExpiresOn = document.getElementById('group-edit-access-expires-on');
  const groupEditIsActive = document.getElementById('group-edit-is-active');
  const groupEditNewPassword = document.getElementById('group-edit-new-password');
  const groupEditSetPasswordBtn = document.getElementById('group-edit-set-password');
  const groupEditError = document.getElementById('group-edit-error');

  let includeInactive = false;
  let searchDebounce = null;
  let toastTimer = null;
  let inviteState = null;

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
      <button type="button" class="pm-action-button pm-action-button--secondary pm-action-button--small pm-admin-toast__action"><span class="pm-action-button__label">${escapeHtml(t('close', 'Close'))}</span></button>
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

  function renderTypeBadge(user) {
    const typeLabel = typeLabelForUser(user);
    const typeIcon = typeIconForUser(user);
    const typeCss = typeCssForUser(user);
    return `
      <span class="pm-admin-badge pm-admin-badge--role-${escapeHtml(typeCss)}">
        <span class="material-symbols-rounded pm-admin-badge__icon" aria-hidden="true">${typeIcon}</span>
        <span>${escapeHtml(typeLabel)}</span>
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
    row.dataset.userId = user.id;
    row.dataset.accountKind = user.account_kind || 'personal';

    // Account column: groups show display_name; personal show "Last, First"
    let accountLabel;
    if (user.account_kind === 'group') {
      accountLabel = user.display_name || user.username || '–';
    } else {
      const last = user.last_name || '';
      const first = user.first_name || '';
      accountLabel = last && first ? `${last}, ${first}` : last || first || user.display_name || '–';
    }

    // Login column: personal = email, group = username
    const loginLabel = user.account_kind === 'group'
      ? (user.username || '–')
      : (user.email || '–');

    // Erstellt column: shown_creator_name (already resolved server-side to responsible admin for groups)
    const createdByLabel = user.shown_creator_name || (user.created_by_is_system ? t('createdBySystem', 'System') : '–');

    // Date: two-line with date and time
    const createdDate = user.created_at ? new Date(user.created_at) : null;
    const dateStr = createdDate && !Number.isNaN(createdDate.getTime())
      ? createdDate.toLocaleDateString(locale)
      : '–';
    const timeStr = createdDate && !Number.isNaN(createdDate.getTime())
      ? createdDate.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })
      : '';

    row.innerHTML = `
      <td><span class="pm-admin-table__primary">${escapeHtml(accountLabel)}</span></td>
      <td>${renderTypeBadge(user)}</td>
      <td><div class="pm-admin-table__email" title="${escapeHtml(loginLabel)}"><span class="pm-admin-table__primary">${escapeHtml(loginLabel)}</span></div></td>
      <td>${renderStatusBadge(user.status_code)}</td>
      <td class="pm-admin-table__desktop"><span class="pm-admin-table__meta">${escapeHtml(formatDate(user.access_expires_on))}</span></td>
      <td class="pm-admin-table__desktop"><span class="pm-admin-table__meta">${escapeHtml(dateStr)}<br><span class="pm-admin-table__meta-sub">${escapeHtml(timeStr)}</span></span></td>
      <td class="pm-admin-table__desktop"><span class="pm-admin-table__meta">${escapeHtml(createdByLabel)}</span></td>
      <td>
        <div class="pm-admin-table__actions">
          <button class="pm-action-button pm-action-button--secondary pm-action-button--small pm-admin-table__action edit-user-btn" type="button" data-id="${escapeHtml(user.id)}" data-kind="${escapeHtml(user.account_kind || 'personal')}" title="${escapeHtml(t('editTitle', 'Edit user'))}" aria-label="${escapeHtml(t('editTitle', 'Edit user'))}">
            <span class="material-symbols-rounded pm-interaction__icon pm-interaction__icon--leading" aria-hidden="true">edit</span>
            <span class="pm-action-button__label">${escapeHtml(t('editActionShort', 'Edit'))}</span>
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
    listBody.innerHTML = `<tr><td colspan="8" class="pm-admin-table__empty">${escapeHtml(t('loading', 'Loading...'))}</td></tr>`;
    syncTableScrollState();
  }

  function syncTableScrollState() {
    if (!tableWrap) {
      return;
    }
    const hasOverflow = tableWrap.scrollWidth > tableWrap.clientWidth + 1;
    const atStart = tableWrap.scrollLeft <= 1;
    const atEnd = tableWrap.scrollLeft + tableWrap.clientWidth >= tableWrap.scrollWidth - 1;
    tableWrap.dataset.overflowX = hasOverflow ? 'true' : 'false';
    tableWrap.dataset.overflowStart = hasOverflow && !atStart ? 'true' : 'false';
    tableWrap.dataset.overflowEnd = hasOverflow && !atEnd ? 'true' : 'false';
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

  function showGroupEditError(message) {
    if (!groupEditError) {
      showToast(message, 'error');
      return;
    }
    const el = groupEditError.querySelector('.pm-admin-alert__text');
    if (el) el.textContent = message;
    groupEditError.hidden = false;
  }

  function clearGroupEditError() {
    if (groupEditError) groupEditError.hidden = true;
  }

  function showCreateGroupError(message) {
    if (!createGroupError) {
      showToast(message, 'error');
      return;
    }
    const el = createGroupError.querySelector('.pm-admin-alert__text');
    if (el) el.textContent = message;
    createGroupError.hidden = false;
  }

  function clearCreateGroupError() {
    if (createGroupError) createGroupError.hidden = true;
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
    inviteState = {
      userId: payload.user && payload.user.id ? payload.user.id : '',
      recipient: payload.inviteMailRecipient || '',
      replyTo: payload.inviteReplyTo || '',
      mailLanguage: payload.inviteMailLanguage || uiLang || 'de',
      mailPurpose: payload.inviteMailPurpose || 'invite',
    };
    if (inviteTitle && payload.mailPreviewTitle) {
      inviteTitle.textContent = payload.mailPreviewTitle;
    }
    if (inviteIntro && payload.mailPreviewIntro) {
      inviteIntro.textContent = payload.mailPreviewIntro;
    }
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
    if (inviteSendStatus) {
      inviteSendStatus.hidden = true;
      inviteSendStatus.textContent = '';
    }
  }

  function showInviteSendStatus(message, type = 'success') {
    if (!inviteSendStatus) {
      showToast(message, type);
      return;
    }
    inviteSendStatus.textContent = message;
    inviteSendStatus.hidden = false;
    inviteSendStatus.dataset.status = type;
  }

  function sendInviteMail() {
    if (!inviteState || !inviteState.userId || !sendInviteMailBtn) {
      return;
    }
    const originalLabel = sendInviteMailBtn.textContent;
    sendInviteMailBtn.disabled = true;
    sendInviteMailBtn.textContent = t('sendMailSending', 'Sending email ...');

    fetch(buildAdminUrl(`/admin/users/${encodeURIComponent(inviteState.userId)}/send-invite`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRF-TOKEN': getCsrfToken(),
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        recipient: inviteState.recipient,
        subject: inviteMailSubject ? inviteMailSubject.value : '',
        body: inviteMailBody ? inviteMailBody.value : '',
        mail_ui_lang: inviteState.mailLanguage,
        purpose: inviteState.mailPurpose,
      }),
    })
      .then((response) => response.json().then((payload) => ({ ok: response.ok, payload })))
      .then(({ ok, payload }) => {
        if (!ok || !payload.ok) {
          throw new Error(payload.error || t('sendMailFailed', 'Email could not be sent. Please use the manual copy fallback.'));
        }
        const message = payload.message || t('sendMailSuccess', 'Email sent.');
        showInviteSendStatus(message, 'success');
        showToast(message, 'success');
      })
      .catch((error) => {
        const message = error.message || t('sendMailFailed', 'Email could not be sent. Please use the manual copy fallback.');
        showInviteSendStatus(message, 'error');
        showToast(message, 'error');
      })
      .finally(() => {
        sendInviteMailBtn.disabled = false;
        sendInviteMailBtn.textContent = originalLabel || t('sendMail', 'Send email');
      });
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

  // ── Load admins list for responsible-admin dropdowns ─────────────────────

  function loadAdminsIntoSelect(selectEl, selectedId) {
    if (!selectEl) return;
    fetch(buildAdminUrl('/admin/admins'), {
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    })
      .then((r) => r.json())
      .then((payload) => {
        const currentVal = selectedId || payload.current_admin_id || '';
        const placeholder = text.responsibleAdminPlaceholder || '–';
        selectEl.innerHTML = `<option value="">${escapeHtml(placeholder)}</option>`;
        (payload.admins || []).forEach((admin) => {
          const opt = document.createElement('option');
          opt.value = admin.id;
          opt.textContent = admin.display_name || admin.id;
          if (admin.id === currentVal) opt.selected = true;
          selectEl.appendChild(opt);
        });
      })
      .catch((err) => console.error('Failed to load admins:', err));
  }

  // ── Personal account edit dialog ─────────────────────────────────────────

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
        if (editUserId) editUserId.value = user.id;
        if (editFirstName) editFirstName.value = user.first_name || '';
        if (editLastName) editLastName.value = user.last_name || '';
        if (editEmail) editEmail.value = user.email || '';
        if (editAccessExpiresOn) editAccessExpiresOn.value = user.access_expires_on || '';
        if (editRole) editRole.value = user.role;
        syncExpiryFieldForRole(editRole, editAccessExpiresOn);
        if (editIsActive) editIsActive.checked = Boolean(user.is_active);
        setDialogOpen(editDialog, true);
      })
      .catch((error) => {
        console.error(error);
        showToast(error.message || t('loadError', 'Could not load users.'), 'error');
      });
  }

  // ── Group account edit dialog ─────────────────────────────────────────────

  function openGroupEditDialog(userId) {
    if (!userId) return;
    clearGroupEditError();
    fetch(buildAdminUrl(`/admin/users/${encodeURIComponent(userId)}`), {
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    })
      .then((r) => {
        if (!r.ok) throw new Error(t('loadError', 'Could not load users.'));
        return r.json();
      })
      .then((user) => {
        if (groupEditUserId) groupEditUserId.value = user.id;
        if (groupEditDisplayName) groupEditDisplayName.value = user.display_name || '';
        if (groupEditAccessExpiresOn) groupEditAccessExpiresOn.value = user.access_expires_on || '';
        if (groupEditIsActive) groupEditIsActive.checked = Boolean(user.is_active);
        if (groupEditNewPassword) groupEditNewPassword.value = '';
        loadAdminsIntoSelect(groupEditResponsibleAdmin, user.responsible_admin_user_id || '');
        setDialogOpen(groupEditDialog, true);
      })
      .catch((err) => {
        showToast(err.message || t('loadError', 'Could not load users.'), 'error');
      });
  }

  function bindEditButtons() {
    document.querySelectorAll('.edit-user-btn').forEach((button) => {
      button.addEventListener('click', () => {
        const kind = button.dataset.kind || 'personal';
        if (kind === 'group') {
          openGroupEditDialog(button.dataset.id);
        } else {
          openEditDialog(button.dataset.id);
        }
      });
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
          listBody.innerHTML = `<tr><td colspan="8" class="pm-admin-table__empty">${escapeHtml(t('noUsers', 'No users found.'))}</td></tr>`;
          return;
        }
        payload.items.forEach((user) => listBody.appendChild(renderRow(user)));
        bindEditButtons();
        syncTableScrollState();
      })
      .catch((error) => {
        console.error(error);
        listBody.innerHTML = `<tr><td colspan="8" class="pm-admin-table__empty">${escapeHtml(error.message || t('loadError', 'Could not load users.'))}</td></tr>`;
      });
  }

  // ── Save personal account edit ────────────────────────────────────────────

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

  // ── Save group account edit ───────────────────────────────────────────────

  function saveGroupEdit() {
    if (!groupEditUserId || !groupEditUserId.value) return;
    clearGroupEditError();
    const displayName = groupEditDisplayName ? groupEditDisplayName.value.trim() : '';
    if (!displayName) {
      showGroupEditError(t('requiredNames', 'A group name is required.'));
      return;
    }
    const originalLabel = saveGroupEditBtn ? saveGroupEditBtn.textContent : '';
    if (saveGroupEditBtn) {
      saveGroupEditBtn.disabled = true;
      saveGroupEditBtn.textContent = t('saving', 'Saving...');
    }
    fetch(buildAdminUrl(`/admin/groups/${encodeURIComponent(groupEditUserId.value)}`), {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRF-TOKEN': getCsrfToken(),
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        display_name: displayName,
        is_active: groupEditIsActive ? groupEditIsActive.checked : true,
        access_expires_on: groupEditAccessExpiresOn ? groupEditAccessExpiresOn.value : '',
        responsible_admin_user_id: groupEditResponsibleAdmin ? groupEditResponsibleAdmin.value : '',
      }),
    })
      .then((r) => r.json())
      .then((payload) => {
        if (!payload.ok) throw new Error(payload.error || t('networkError', 'Network error.'));
        setDialogOpen(groupEditDialog, false);
        reload();
        showToast(t('updated', 'Updated.'), 'success');
      })
      .catch((err) => {
        showGroupEditError(err.message || t('networkError', 'Network error.'));
      })
      .finally(() => {
        if (saveGroupEditBtn) {
          saveGroupEditBtn.disabled = false;
          saveGroupEditBtn.textContent = originalLabel || t('save', 'Save');
        }
      });
  }

  function setGroupPassword() {
    if (!groupEditUserId || !groupEditUserId.value) return;
    const pw = groupEditNewPassword ? groupEditNewPassword.value : '';
    if (!pw) {
      showGroupEditError(t('groupPasswordRequired', 'Please enter a password.'));
      return;
    }
    const originalLabel = groupEditSetPasswordBtn ? groupEditSetPasswordBtn.textContent : '';
    if (groupEditSetPasswordBtn) {
      groupEditSetPasswordBtn.disabled = true;
      groupEditSetPasswordBtn.textContent = t('saving', 'Saving...');
    }
    fetch(buildAdminUrl(`/admin/groups/${encodeURIComponent(groupEditUserId.value)}/set-password`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRF-TOKEN': getCsrfToken(),
      },
      credentials: 'same-origin',
      body: JSON.stringify({ password: pw }),
    })
      .then((r) => r.json())
      .then((payload) => {
        if (!payload.ok) throw new Error(payload.error || t('networkError', 'Network error.'));
        if (groupEditNewPassword) groupEditNewPassword.value = '';
        showToast(t('groupPasswordSet', 'Password set.'), 'success');
      })
      .catch((err) => {
        showGroupEditError(err.message || t('networkError', 'Network error.'));
      })
      .finally(() => {
        if (groupEditSetPasswordBtn) {
          groupEditSetPasswordBtn.disabled = false;
          groupEditSetPasswordBtn.textContent = originalLabel || t('setPassword', 'Set password');
        }
      });
  }

  function selectedEditMailLanguage() {
    return editMailLanguage && editMailLanguage.value ? editMailLanguage.value : uiLang || 'de';
  }

  function prepareMail(purpose) {
    if (!editUserId || !editUserId.value) {
      return;
    }
    const actionButton = purpose === 'invite' ? editSendInviteBtn : editResetPasswordBtn;
    const originalLabel = actionButton ? actionButton.textContent : '';
    if (actionButton) {
      actionButton.disabled = true;
      actionButton.textContent = t('sending', 'Preparing...');
    }

    fetch(buildAdminUrl(`/admin/users/${encodeURIComponent(editUserId.value)}/${purpose === 'invite' ? 'invite' : 'reset-password'}`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRF-TOKEN': getCsrfToken(),
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        mail_ui_lang: selectedEditMailLanguage(),
      }),
    })
      .then((response) => response.json())
      .then((payload) => {
        if (!payload.ok) {
          throw new Error(payload.error || t('networkError', 'Network error. Please try again.'));
        }
        populateInviteDialog(payload);
        setDialogOpen(editDialog, false);
        setDialogOpen(inviteDialog, true);
        showToast(purpose === 'invite' ? t('invitePrepared', 'Invitation prepared.') : t('resetPrepared', 'Password link prepared.'), 'success');
      })
      .catch((error) => {
        console.error(error);
        showToast(error.message || t('networkError', 'Network error. Please try again.'), 'error');
      })
      .finally(() => {
        if (actionButton) {
          actionButton.disabled = false;
          actionButton.textContent = originalLabel || (purpose === 'invite' ? t('sendInvite', 'Send invitation') : t('resetPassword', 'Prepare new link'));
        }
      });
  }

  // ── Event bindings ────────────────────────────────────────────────────────

  if (refreshBtn) refreshBtn.addEventListener('click', reload);

  if (filterInactiveBtn) {
    filterInactiveBtn.addEventListener('click', () => {
      includeInactive = !includeInactive;
      filterInactiveBtn.classList.toggle('is-active', includeInactive);
      filterInactiveBtn.setAttribute('aria-pressed', includeInactive ? 'true' : 'false');
      const icon = filterInactiveBtn.querySelector('.material-symbols-rounded');
      if (icon) icon.textContent = includeInactive ? 'visibility' : 'visibility_off';
      reload();
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      window.clearTimeout(searchDebounce);
      searchDebounce = window.setTimeout(reload, 250);
    });
  }

  if (sortSelect) sortSelect.addEventListener('change', reload);

  // Personal account creation
  if (createBtn) {
    createBtn.addEventListener('click', () => {
      if (createForm) createForm.reset();
      syncExpiryFieldForRole(document.getElementById('new-role'), document.getElementById('new-access-expires-on'));
      setDialogOpen(createDialog, true);
    });
  }
  if (cancelCreateBtn) cancelCreateBtn.addEventListener('click', () => setDialogOpen(createDialog, false));
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

  // Group account creation
  if (createGroupBtn) {
    createGroupBtn.addEventListener('click', () => {
      if (createGroupForm) createGroupForm.reset();
      clearCreateGroupError();
      loadAdminsIntoSelect(groupResponsibleAdminSelect, '');
      setDialogOpen(createGroupDialog, true);
    });
  }
  if (cancelCreateGroupBtn) cancelCreateGroupBtn.addEventListener('click', () => setDialogOpen(createGroupDialog, false));
  if (submitCreateGroupBtn) {
    submitCreateGroupBtn.addEventListener('click', () => {
      clearCreateGroupError();
      if (!createGroupForm) return;
      const formData = new FormData(createGroupForm);
      const displayName = (formData.get('display_name') || '').trim();
      const loginName = (formData.get('login_name') || '').trim();
      const password = formData.get('password') || '';
      const passwordConfirm = formData.get('password_confirm') || '';
      const responsibleAdminId = formData.get('responsible_admin_user_id') || '';
      const accessExpiresOn = formData.get('access_expires_on') || '';

      if (!displayName) {
        showCreateGroupError(t('requiredNames', 'Group name is required.'));
        return;
      }
      if (!loginName) {
        showCreateGroupError(t('requiredNames', 'Login name is required.'));
        return;
      }
      if (!password) {
        showCreateGroupError(t('requiredNames', 'Password is required.'));
        return;
      }
      if (password !== passwordConfirm) {
        showCreateGroupError(t('passwordMismatch', 'Passwords do not match.'));
        return;
      }

      const originalLabel = submitCreateGroupBtn.textContent;
      submitCreateGroupBtn.disabled = true;
      submitCreateGroupBtn.textContent = t('saving', 'Saving...');

      fetch(buildAdminUrl('/admin/groups'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          'X-CSRF-TOKEN': getCsrfToken(),
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          display_name: displayName,
          login_name: loginName,
          password,
          responsible_admin_user_id: responsibleAdminId,
          access_expires_on: accessExpiresOn,
        }),
      })
        .then((r) => r.json())
        .then((payload) => {
          if (!payload.ok) throw new Error(payload.error || t('networkError', 'Network error.'));
          setDialogOpen(createGroupDialog, false);
          reload();
          showToast(t('groupCreated', 'Group account created.'), 'success');
        })
        .catch((err) => {
          showCreateGroupError(err.message || t('networkError', 'Network error.'));
        })
        .finally(() => {
          submitCreateGroupBtn.disabled = false;
          submitCreateGroupBtn.textContent = originalLabel;
        });
    });
  }

  // Invite dialog buttons
  if (copyInviteBtn) copyInviteBtn.addEventListener('click', () => copyText(inviteLinkCode ? inviteLinkCode.textContent || '' : '', t('copiedLink', 'Link copied.')));
  if (sendInviteMailBtn) sendInviteMailBtn.addEventListener('click', sendInviteMail);
  if (copyInviteMailBtn) {
    copyInviteMailBtn.addEventListener('click', () => {
      const mailText = `${inviteMailSubject ? inviteMailSubject.value : ''}\n\n${inviteMailBody ? inviteMailBody.value : ''}`.trim();
      copyText(mailText, t('copiedMail', 'Email copied.'));
    });
  }
  if (closeInviteBtn) closeInviteBtn.addEventListener('click', () => setDialogOpen(inviteDialog, false));

  // Personal account edit buttons
  if (cancelEditBtn) cancelEditBtn.addEventListener('click', () => setDialogOpen(editDialog, false));
  if (saveEditBtn) saveEditBtn.addEventListener('click', saveEdit);
  if (editRole) editRole.addEventListener('change', () => syncExpiryFieldForRole(editRole, editAccessExpiresOn));
  if (editSendInviteBtn) editSendInviteBtn.addEventListener('click', () => prepareMail('invite'));
  if (editResetPasswordBtn) editResetPasswordBtn.addEventListener('click', () => prepareMail('reset'));

  // Personal create role/expiry sync
  const createRole = document.getElementById('new-role');
  const createExpiry = document.getElementById('new-access-expires-on');
  if (createRole) {
    createRole.addEventListener('change', () => syncExpiryFieldForRole(createRole, createExpiry));
    syncExpiryFieldForRole(createRole, createExpiry);
  }

  // Group account edit buttons
  if (cancelGroupEditBtn) cancelGroupEditBtn.addEventListener('click', () => setDialogOpen(groupEditDialog, false));
  if (saveGroupEditBtn) saveGroupEditBtn.addEventListener('click', saveGroupEdit);
  if (groupEditSetPasswordBtn) groupEditSetPasswordBtn.addEventListener('click', setGroupPassword);

  if (tableWrap) {
    tableWrap.addEventListener('scroll', syncTableScrollState, { passive: true });
    window.addEventListener('resize', syncTableScrollState);
  }

  reload();
  syncTableScrollState();
});
