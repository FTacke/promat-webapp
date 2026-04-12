function formatClock(totalSeconds) {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds));
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const seconds = safeSeconds % 60;

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

function formatRate(rate) {
  return `${Number(rate).toFixed(2)}×`;
}

function parseState() {
  const stateElement = document.getElementById('pm-player-state');
  if (!stateElement) {
    return null;
  }

  try {
    const parsed = JSON.parse(stateElement.textContent || '{}');
    return Array.isArray(parsed.speakers) ? parsed : null;
  } catch {
    return null;
  }
}

let playerNavigationController = null;

function currentPlayerPage() {
  return document.querySelector('article.pm-research-page');
}

function setPlayerNavigationPending(isPending) {
  document.documentElement.classList.toggle('pm-player-nav-pending', isPending);
  const page = currentPlayerPage();
  if (!page) {
    return;
  }
  page.classList.toggle('is-player-nav-pending', isPending);
  if (isPending) {
    page.setAttribute('aria-busy', 'true');
    return;
  }
  page.removeAttribute('aria-busy');
}

async function navigatePlayerInPlace(href) {
  if (!href) {
    return false;
  }

  const nextUrl = new URL(href, window.location.href);
  const currentUrl = new URL(window.location.href);
  if (`${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}` === `${currentUrl.pathname}${currentUrl.search}${currentUrl.hash}`) {
    return true;
  }

  if (playerNavigationController) {
    playerNavigationController.abort();
  }

  document.querySelectorAll('[data-player-audio]').forEach((element) => {
    if (typeof element.pause === 'function') {
      element.pause();
    }
  });

  const controller = new AbortController();
  playerNavigationController = controller;
  setPlayerNavigationPending(true);

  try {
    const response = await fetch(nextUrl.toString(), {
      credentials: 'same-origin',
      headers: { 'X-Requested-With': 'promat-player-nav' },
      signal: controller.signal,
    });
    if (!response.ok) {
      throw new Error(`Navigation failed with status ${response.status}`);
    }

    const html = await response.text();
    if (controller.signal.aborted) {
      return false;
    }

    const parsed = new DOMParser().parseFromString(html, 'text/html');
    const nextPage = parsed.querySelector('article.pm-research-page');
    const currentPage = currentPlayerPage();
    if (!nextPage || !currentPage) {
      throw new Error('Player page markup is missing.');
    }

    currentPage.replaceWith(document.importNode(nextPage, true));

    const currentState = document.getElementById('pm-player-state');
    if (currentState) {
      currentState.remove();
    }
    const nextState = parsed.getElementById('pm-player-state');
    if (nextState) {
      document.body.appendChild(document.importNode(nextState, true));
    }

    if (parsed.title) {
      document.title = parsed.title;
    }
    window.history.replaceState({ playerNavigation: true }, '', `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`);

    initSetSelect();
    init();
    return true;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return false;
    }
    window.location.assign(nextUrl.toString());
    return false;
  } finally {
    if (playerNavigationController === controller) {
      playerNavigationController = null;
    }
    setPlayerNavigationPending(false);
  }
}

function initSetSelect() {
  const select = document.querySelector('[data-player-set-select]');
  if (!select) {
    return;
  }

  if (select.dataset.playerSetSelectBound === 'true') {
    return;
  }
  select.dataset.playerSetSelectBound = 'true';

  select.addEventListener('change', () => {
    const nextHref = select.value;
    if (!nextHref || nextHref === window.location.href) {
      return;
    }
    void navigatePlayerInPlace(nextHref);
  });
}

function bindInPlacePlayerNavigation(scope) {
  const links = Array.from(scope.querySelectorAll(
    '.pm-player-session-picker__option[href], .pm-player-material-strip a[href], .pm-player-view-switch a[href]'
  ));

  for (const link of links) {
    if (link.dataset.playerNavBound === 'true') {
      continue;
    }
    link.dataset.playerNavBound = 'true';
    link.addEventListener('click', (event) => {
      if (
        event.defaultPrevented
        || event.button !== 0
        || event.metaKey
        || event.ctrlKey
        || event.shiftKey
        || event.altKey
      ) {
        return;
      }
      event.preventDefault();
      void navigatePlayerInPlace(link.href);
    });
  }
}

function findActiveItem(items, currentMs) {
  for (const item of items) {
    if (currentMs >= item.startMs && currentMs <= item.endMs) {
      return item.itemId;
    }
  }

  if (!items.length || currentMs < items[0].startMs) {
    return null;
  }

  return items[items.length - 1].itemId;
}

function init() {
  const root = document.querySelector('[data-player-root]');
  const state = parseState();
  const runtimeInner = root?.closest('.pm-player-runtime__inner') || null;
  const runtimeScope = runtimeInner || root;
  if (!root || !state) {
    return;
  }

  bindInPlacePlayerNavigation(document);

  const audioElements = Array.from(root.querySelectorAll('[data-player-audio][data-speaker-key]'));
  const toggle = root.querySelector('[data-player-toggle]');
  const toggleIcon = root.querySelector('[data-player-toggle-icon]');
  const progress = root.querySelector('[data-player-progress]');
  const volume = root.querySelector('[data-player-volume]');
  const volumeLabel = root.querySelector('[data-player-volume-label]');
  const rateSlider = root.querySelector('[data-player-rate-slider]');
  const rateValue = root.querySelector('[data-player-rate-value]');
  const currentLabel = root.querySelector('[data-player-current]');
  const durationLabel = root.querySelector('[data-player-duration]');
  const comparePanel = root.querySelector('[data-player-compare-panel]');
  const compareAddButtons = Array.from(runtimeScope.querySelectorAll('[data-player-compare-add]'));
  const compareRemoveButtons = Array.from(runtimeScope.querySelectorAll('[data-player-compare-remove]'));
  const sequenceToggle = root.querySelector('[data-player-sequence-toggle]');
  const sequenceWrap = root.querySelector('[data-player-sequence-wrap]');
  const sessionMenus = Array.from(runtimeScope.querySelectorAll('[data-player-session-menu]'));
  const speakerCards = Array.from(runtimeScope.querySelectorAll('[data-player-speaker-card]'));
  const secondaryCard = runtimeScope.querySelector('[data-player-speaker-card="secondary"]');
  const itemElements = Array.from(root.querySelectorAll('[data-player-item][data-speaker-key][data-item-id]'));

  if (!toggle || !progress || !currentLabel || !durationLabel || !volume || !volumeLabel || !rateSlider) {
    return;
  }

  const playLabel = toggle.dataset.playLabel || '';
  const pauseLabel = toggle.dataset.pauseLabel || '';
  const desktopMedia = window.matchMedia(`(min-width: ${Number(state.mobileMinWidth || 900)}px)`);
  const audioMap = new Map(audioElements.map((element) => [element.dataset.speakerKey, element]));
  const speakerState = new Map(
    state.speakers.map((speaker) => [
      speaker.key,
      {
        ...speaker,
        itemsById: new Map((speaker.items || []).map((item) => [item.itemId, item])),
      },
    ]),
  );
  const itemMap = new Map();
  for (const element of itemElements) {
    const speakerKey = element.dataset.speakerKey;
    const itemId = element.dataset.itemId;
    if (!speakerKey || !itemId) {
      continue;
    }
    if (!itemMap.has(speakerKey)) {
      itemMap.set(speakerKey, new Map());
    }
    const speakerItems = itemMap.get(speakerKey);
    const existing = speakerItems.get(itemId) || [];
    existing.push(element);
    speakerItems.set(itemId, existing);
  }

  let activeSpeakerKey = 'primary';
  let clipCleanup = null;
  let sequenceToken = 0;
  let currentRate = Number(state.defaultRate || 1);
  state.compareOpen = Boolean(state.compareOpen);
  state.canCompare = Boolean(state.canCompare);
  state.lastCompareMode = state.requestedMode === 'manual' ? 'manual' : 'sequence';

  function compareIsReady() {
    return Boolean(state.compareReady && speakerState.has('secondary') && audioMap.has('secondary'));
  }

  function compareIsOpen() {
    return Boolean(state.canCompare && state.compareOpen);
  }

  function effectiveMode() {
    if (!compareIsReady() || !compareIsOpen() || !desktopMedia.matches) {
      return 'single';
    }
    return state.requestedMode || 'single';
  }

  function activeAudio() {
    return audioMap.get(activeSpeakerKey) || audioMap.get('primary') || null;
  }

  function clearClipPlayback() {
    if (typeof clipCleanup === 'function') {
      clipCleanup();
      clipCleanup = null;
    }
  }

  function cancelSequence() {
    sequenceToken += 1;
    clearClipPlayback();
  }

  function pauseOtherAudios(exceptSpeakerKey) {
    for (const [speakerKey, audio] of audioMap.entries()) {
      if (speakerKey === exceptSpeakerKey) {
        continue;
      }
      audio.pause();
    }
  }

  function applySharedAudioSettings() {
    const nextVolume = Number(volume.value) / 100;
    for (const audio of audioMap.values()) {
      audio.volume = nextVolume;
      audio.playbackRate = currentRate;
      audio.defaultPlaybackRate = currentRate;
    }
    volumeLabel.textContent = `${Math.round(nextVolume * 100)}%`;
  }

  function rateIndexForValue(rate) {
    const options = Array.isArray(state.rateOptions) ? state.rateOptions : [];
    const exactIndex = options.findIndex((optionRate) => Math.abs(Number(optionRate) - rate) < 0.001);
    return exactIndex >= 0 ? exactIndex : 0;
  }

  function syncRateSlider() {
    rateSlider.value = String(rateIndexForValue(currentRate));
    if (rateValue) {
      rateValue.textContent = formatRate(currentRate);
    }
  }

  function syncToggleLabel() {
    const currentAudio = activeAudio();
    const nextLabel = !currentAudio || currentAudio.paused ? playLabel : pauseLabel;
    toggle.setAttribute('aria-label', nextLabel);
    toggle.setAttribute('title', nextLabel);
    if (toggleIcon) {
      toggleIcon.classList.toggle('pm-icon-mask--play', nextLabel === playLabel);
      toggleIcon.classList.toggle('pm-icon-mask--pause', nextLabel === pauseLabel);
    }
  }

  function syncProgress() {
    const currentAudio = activeAudio();
    const duration = currentAudio && Number.isFinite(currentAudio.duration) ? currentAudio.duration : 0;
    const currentTime = currentAudio && Number.isFinite(currentAudio.currentTime) ? currentAudio.currentTime : 0;
    currentLabel.textContent = formatClock(currentTime);
    durationLabel.textContent = formatClock(duration);

    if (duration > 0) {
      progress.disabled = false;
      progress.value = String(Math.min(1000, Math.max(0, Math.round((currentTime / duration) * 1000))));
    } else {
      progress.disabled = true;
      progress.value = '0';
    }
  }

  function setSpeakerHighlights() {
    for (const card of speakerCards) {
      const isCurrent = card.dataset.playerSpeakerCard === activeSpeakerKey;
      card.classList.toggle('is-selected', isCurrent);
    }
  }

  function syncCompareSurface() {
    const compareOpen = compareIsOpen();
    const compareActive = compareOpen && compareIsReady() && desktopMedia.matches;
    root.dataset.playerCompareOpen = compareOpen ? 'true' : 'false';
    root.dataset.playerCompareReady = compareIsReady() ? 'true' : 'false';
    root.dataset.playerCompareActive = compareActive ? 'true' : 'false';
    if (runtimeInner) {
      runtimeInner.dataset.playerCompareOpen = root.dataset.playerCompareOpen;
      runtimeInner.dataset.playerCompareReady = root.dataset.playerCompareReady;
    }

    if (secondaryCard) {
      secondaryCard.hidden = !compareOpen;
    }
    if (comparePanel) {
      comparePanel.hidden = !compareActive;
    }
    if (sequenceWrap) {
      sequenceWrap.hidden = !compareActive;
    }

    for (const button of compareAddButtons) {
      button.hidden = compareOpen;
    }
    for (const button of compareRemoveButtons) {
      button.hidden = !compareOpen;
    }
  }

  function setActiveSpeaker(nextSpeakerKey) {
    if (!audioMap.has(nextSpeakerKey)) {
      activeSpeakerKey = 'primary';
    } else {
      activeSpeakerKey = nextSpeakerKey;
    }
    setSpeakerHighlights();
    syncProgress();
    syncToggleLabel();
  }

  function syncPlaybackMode() {
    const nextMode = effectiveMode();
    root.dataset.playerMode = nextMode;
    if (sequenceToggle) {
      const isSequence = nextMode === 'sequence';
      sequenceToggle.checked = isSequence;
      sequenceToggle.disabled = !compareIsReady() || !compareIsOpen() || !desktopMedia.matches;
      root.dataset.playerSequenceEnabled = isSequence ? 'true' : 'false';
    }
  }

  function setSequenceEnabled(enabled, nextHref) {
    if (!compareIsReady() || !compareIsOpen()) {
      syncPlaybackMode();
      return;
    }

    const normalizedMode = enabled ? 'sequence' : 'manual';
    if (state.requestedMode === normalizedMode) {
      syncPlaybackMode();
      return;
    }

    cancelSequence();
    for (const audio of audioMap.values()) {
      audio.pause();
    }

    state.requestedMode = normalizedMode;
    state.lastCompareMode = normalizedMode;
    syncCompareSurface();
    syncPlaybackMode();
    syncProgress();
    syncToggleLabel();
    syncActiveItems();

    if (nextHref) {
      window.history.replaceState({ compareMode: normalizedMode }, '', nextHref);
    }
  }

  function openCompare() {
    if (!state.canCompare) {
      return;
    }

    state.compareOpen = true;
    if (compareIsReady()) {
      state.requestedMode = state.lastCompareMode === 'manual' ? 'manual' : 'sequence';
      const nextHref = state.modeHrefs?.[state.requestedMode] || null;
      if (nextHref) {
        window.history.replaceState({ compareMode: state.requestedMode }, '', nextHref);
      }
    }

    syncCompareSurface();
    syncPlaybackMode();
    syncProgress();
    syncToggleLabel();
    syncActiveItems();

    if (secondaryCard && !compareIsReady()) {
      const secondaryMenu = secondaryCard.querySelector('[data-player-session-menu]');
      if (secondaryMenu) {
        secondaryMenu.open = true;
        const summary = secondaryMenu.querySelector('summary');
        if (summary) {
          summary.focus();
        }
      }
    }
  }

  function closeCompare() {
    state.lastCompareMode = effectiveMode() === 'manual' ? 'manual' : 'sequence';

    cancelSequence();
    for (const audio of audioMap.values()) {
      audio.pause();
    }

    state.compareOpen = false;
    state.requestedMode = state.lastCompareMode;
    setActiveSpeaker('primary');
    syncCompareSurface();
    syncPlaybackMode();
    syncProgress();
    syncToggleLabel();
    syncActiveItems();

    for (const menu of sessionMenus) {
      if (menu.dataset.playerSessionMenu === 'secondary') {
        menu.open = false;
      }
    }

    if (state.singleViewHref) {
      window.history.replaceState({ compareMode: 'single' }, '', state.singleViewHref);
    }
  }

  function setItemActiveState(speakerKey, nextItemId) {
    const speakerItems = itemMap.get(speakerKey);
    if (!speakerItems) {
      return;
    }
    for (const [itemId, elements] of speakerItems.entries()) {
      for (const element of elements) {
        element.classList.toggle('is-active', itemId === nextItemId);
      }
    }
  }

  function syncActiveItems() {
    for (const [speakerKey, speaker] of speakerState.entries()) {
      const audio = audioMap.get(speakerKey);
      const items = speaker.items || [];
      const nextItemId = !audio ? null : findActiveItem(items, Math.round((audio.currentTime || 0) * 1000));
      setItemActiveState(speakerKey, nextItemId);
    }
  }

  function revealFocusedItem() {
    const focusedItemId = state.focusedItemId;
    if (!focusedItemId) {
      return;
    }
    const focusRows = Array.from(root.querySelectorAll('[data-player-focus-item]'));
    const focusRow = focusRows.find((element) => element.dataset.playerFocusItem === focusedItemId) || null;
    const primaryItems = itemMap.get('primary');
    const focusedElements = primaryItems?.get(focusedItemId);
    const element = Array.isArray(focusedElements) ? focusedElements[0] : null;
    if (!focusRow && !element) {
      return;
    }
    if (focusRow) {
      focusRow.classList.add('is-focused');
      focusRow.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
    if (element) {
      element.classList.add('is-active');
    }
  }

  function playClip(speakerKey, itemId) {
    const speaker = speakerState.get(speakerKey);
    const item = speaker?.itemsById?.get(itemId);
    const audio = audioMap.get(speakerKey);
    if (!speaker || !item || !audio) {
      return Promise.resolve(false);
    }

    clearClipPlayback();
    pauseOtherAudios(speakerKey);
    setActiveSpeaker(speakerKey);
    audio.currentTime = item.startMs / 1000;
    syncProgress();
    syncActiveItems();

    return new Promise((resolve) => {
      let settled = false;
      const endSeconds = item.endMs / 1000;

      const finish = (completed) => {
        if (settled) {
          return;
        }
        settled = true;
        audio.removeEventListener('timeupdate', onTimeUpdate);
        audio.removeEventListener('ended', onEnded);
        if (clipCleanup === cleanup) {
          clipCleanup = null;
        }
        syncToggleLabel();
        syncProgress();
        syncActiveItems();
        resolve(completed);
      };

      const onTimeUpdate = () => {
        if ((audio.currentTime || 0) >= endSeconds) {
          audio.pause();
          audio.currentTime = endSeconds;
          finish(true);
        }
      };

      const onEnded = () => finish(true);
      const cleanup = () => finish(false);

      clipCleanup = cleanup;
      audio.addEventListener('timeupdate', onTimeUpdate);
      audio.addEventListener('ended', onEnded);
      audio.play().catch(() => finish(false));
    });
  }

  async function startSequence(itemId) {
    const token = ++sequenceToken;
    const primaryAvailable = speakerState.get('primary')?.itemsById?.has(itemId);
    const secondaryAvailable = speakerState.get('secondary')?.itemsById?.has(itemId);
    if (!compareIsReady() || (!primaryAvailable && !secondaryAvailable)) {
      return;
    }

    if (primaryAvailable) {
      const completed = await playClip('primary', itemId);
      if (!completed || token !== sequenceToken) {
        return;
      }
    }
    if (secondaryAvailable) {
      await playClip('secondary', itemId);
    }
  }

  toggle.addEventListener('click', async () => {
    const currentAudio = activeAudio();
    if (!currentAudio) {
      return;
    }

    if (!currentAudio.paused) {
      cancelSequence();
      currentAudio.pause();
      syncToggleLabel();
      return;
    }

    pauseOtherAudios(activeSpeakerKey);
    try {
      await currentAudio.play();
    } catch {
      syncToggleLabel();
    }
  });

  progress.addEventListener('input', () => {
    cancelSequence();
    const currentAudio = activeAudio();
    const duration = currentAudio && Number.isFinite(currentAudio.duration) ? currentAudio.duration : 0;
    if (duration <= 0) {
      return;
    }

    currentAudio.currentTime = (Number(progress.value) / 1000) * duration;
    syncProgress();
    syncActiveItems();
  });

  volume.addEventListener('input', applySharedAudioSettings);

  rateSlider.addEventListener('input', () => {
    const nextIndex = Number(rateSlider.value || '0');
    currentRate = Number(state.rateOptions?.[nextIndex] || currentRate);
    applySharedAudioSettings();
    syncRateSlider();
  });

  for (const button of compareAddButtons) {
    button.addEventListener('click', () => {
      openCompare();
    });
  }

  for (const button of compareRemoveButtons) {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      closeCompare();
    });
  }

  if (sequenceToggle) {
    sequenceToggle.addEventListener('change', () => {
      const nextMode = sequenceToggle.checked ? 'sequence' : 'manual';
      setSequenceEnabled(sequenceToggle.checked, state.modeHrefs?.[nextMode] || null);
    });
  }

  for (const element of itemElements) {
    const button = element.querySelector('[data-player-seek]');
    if (!button) {
      continue;
    }

    button.addEventListener('click', async () => {
      const speakerKey = element.dataset.speakerKey || 'primary';
      const itemId = element.dataset.itemId;
      if (!itemId) {
        return;
      }

      if (effectiveMode() === 'sequence' && compareIsReady()) {
        await startSequence(itemId);
        return;
      }

      cancelSequence();
      await playClip(speakerKey, itemId);
    });
  }

  for (const [speakerKey, audio] of audioMap.entries()) {
    audio.addEventListener('loadedmetadata', syncProgress);
    audio.addEventListener('durationchange', syncProgress);
    audio.addEventListener('timeupdate', () => {
      if (speakerKey === activeSpeakerKey) {
        syncProgress();
      }
      syncActiveItems();
    });
    audio.addEventListener('play', () => {
      pauseOtherAudios(speakerKey);
      setActiveSpeaker(speakerKey);
      syncToggleLabel();
    });
    audio.addEventListener('pause', syncToggleLabel);
    audio.addEventListener('ended', () => {
      syncToggleLabel();
      syncProgress();
      syncActiveItems();
    });
  }

  const handleViewportChange = () => {
    if (effectiveMode() === 'single' && activeSpeakerKey === 'secondary') {
      setActiveSpeaker('primary');
    }
    syncCompareSurface();
    syncPlaybackMode();
    syncProgress();
    syncToggleLabel();
  };

  if (typeof desktopMedia.addEventListener === 'function') {
    desktopMedia.addEventListener('change', handleViewportChange);
  } else if (typeof desktopMedia.addListener === 'function') {
    desktopMedia.addListener(handleViewportChange);
  }

  applySharedAudioSettings();
  syncRateSlider();
  syncCompareSurface();
  setActiveSpeaker('primary');
  syncPlaybackMode();
  syncToggleLabel();
  syncProgress();
  syncActiveItems();
  revealFocusedItem();
}

document.addEventListener('DOMContentLoaded', () => {
  initSetSelect();
  init();
});