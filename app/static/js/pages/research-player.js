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

function parseState() {
  const stateElement = document.getElementById('pm-player-state');
  if (!stateElement) {
    return null;
  }

  try {
    const parsed = JSON.parse(stateElement.textContent || '{}');
    return Array.isArray(parsed.items) ? parsed : null;
  } catch {
    return null;
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
  if (!root || !state) {
    return;
  }

  const audio = root.querySelector('[data-player-audio]');
  const toggle = root.querySelector('[data-player-toggle]');
  const progress = root.querySelector('[data-player-progress]');
  const currentLabel = root.querySelector('[data-player-current]');
  const durationLabel = root.querySelector('[data-player-duration]');
  const itemElements = Array.from(root.querySelectorAll('[data-player-item]'));
  const itemMap = new Map(itemElements.map((element) => [element.dataset.itemId, element]));

  if (!audio || !toggle || !progress || !currentLabel || !durationLabel) {
    return;
  }

  const playLabel = toggle.dataset.playLabel || 'Play';
  const pauseLabel = toggle.dataset.pauseLabel || 'Pause';
  let activeItemId = null;

  function syncToggleLabel() {
    const nextLabel = audio.paused ? playLabel : pauseLabel;
    toggle.textContent = nextLabel;
    toggle.setAttribute('aria-label', nextLabel);
  }

  function syncProgress() {
    const duration = Number.isFinite(audio.duration) ? audio.duration : 0;
    const currentTime = Number.isFinite(audio.currentTime) ? audio.currentTime : 0;
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

  function setActiveItem(nextItemId) {
    if (activeItemId === nextItemId) {
      return;
    }

    if (activeItemId && itemMap.has(activeItemId)) {
      itemMap.get(activeItemId).classList.remove('is-active');
    }

    activeItemId = nextItemId;
    if (activeItemId && itemMap.has(activeItemId)) {
      itemMap.get(activeItemId).classList.add('is-active');
    }
  }

  function syncActiveItem() {
    setActiveItem(findActiveItem(state.items, Math.round((audio.currentTime || 0) * 1000)));
  }

  toggle.addEventListener('click', async () => {
    if (audio.paused) {
      try {
        await audio.play();
      } catch {
        syncToggleLabel();
      }
      return;
    }

    audio.pause();
  });

  progress.addEventListener('input', () => {
    const duration = Number.isFinite(audio.duration) ? audio.duration : 0;
    if (duration <= 0) {
      return;
    }

    audio.currentTime = (Number(progress.value) / 1000) * duration;
    syncProgress();
    syncActiveItem();
  });

  for (const element of itemElements) {
    const button = element.querySelector('[data-player-seek]');
    if (!button) {
      continue;
    }

    button.addEventListener('click', async () => {
      const startMs = Number(element.dataset.startMs || '0');
      audio.currentTime = startMs / 1000;
      syncProgress();
      syncActiveItem();

      try {
        await audio.play();
      } catch {
        syncToggleLabel();
      }
    });
  }

  audio.addEventListener('loadedmetadata', syncProgress);
  audio.addEventListener('durationchange', syncProgress);
  audio.addEventListener('timeupdate', () => {
    syncProgress();
    syncActiveItem();
  });
  audio.addEventListener('play', syncToggleLabel);
  audio.addEventListener('pause', syncToggleLabel);
  audio.addEventListener('ended', () => {
    syncToggleLabel();
    syncProgress();
  });

  syncToggleLabel();
  syncProgress();
  syncActiveItem();
}

document.addEventListener('DOMContentLoaded', init);