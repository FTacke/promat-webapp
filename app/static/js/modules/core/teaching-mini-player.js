function formatClock(totalSeconds) {
  if (!Number.isFinite(totalSeconds) || totalSeconds <= 0) {
    return '0:00';
  }

  const rounded = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(rounded / 60);
  const seconds = rounded % 60;
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

function getKnownDuration(audio) {
  if (Number.isFinite(audio.duration) && audio.duration > 0) {
    audio.dataset.durationSeconds = String(audio.duration);
    return audio.duration;
  }

  const cachedDuration = Number(audio.dataset.durationSeconds || '');
  if (Number.isFinite(cachedDuration) && cachedDuration > 0) {
    return cachedDuration;
  }

  return 0;
}

const LINKED_AUDIO_PROGRESS_LEAD_FACTOR = 1.08;

let teachingMiniPlayerCounter = 0;

function ensureFeedbackKey(player) {
  if (!player.dataset.audioFeedbackKey) {
    teachingMiniPlayerCounter += 1;
    player.dataset.audioFeedbackKey = `pm-teaching-mini-player-${teachingMiniPlayerCounter}`;
  }

  return player.dataset.audioFeedbackKey;
}

function getPlaybackState(audio, forcedState = '') {
  if (forcedState === 'playing' || forcedState === 'paused' || forcedState === 'idle') {
    return forcedState;
  }

  const currentTime = Number.isFinite(audio.currentTime) ? Math.max(0, audio.currentTime) : 0;
  if (!audio.paused) {
    return 'playing';
  }

  if (audio.ended) {
    return 'idle';
  }

  if (currentTime > 0) {
    return 'paused';
  }

  return 'idle';
}

function prefersReducedMotion() {
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function getPlaybackProgress(audio, leadFactor = 1) {
  const duration = getKnownDuration(audio);
  const currentTime = Number.isFinite(audio.currentTime) ? Math.max(0, audio.currentTime) : 0;
  if (!Number.isFinite(duration) || duration <= 0) {
    return 0;
  }

  const rawProgress = currentTime / duration;
  const visualProgress = Math.min(1, Math.max(0, rawProgress * leadFactor));
  return visualProgress * 100;
}

function getFeedbackTarget(player) {
  const targetId = player.dataset.audioFeedbackTarget || '';
  if (!targetId) {
    return null;
  }

  const target = document.getElementById(targetId);
  return target instanceof HTMLElement ? target : null;
}

function syncLinkedAudioFeedback(player, audio, forcedState = '') {
  const state = getPlaybackState(audio, forcedState);
  const target = getFeedbackTarget(player);
  player.dataset.audioState = state;

  if (!(target instanceof HTMLElement)) {
    return;
  }

  const playerKey = ensureFeedbackKey(player);
  const ownerKey = target.dataset.audioFeedbackOwner || '';
  const progressValue = state === 'idle' ? 0 : getPlaybackProgress(audio, LINKED_AUDIO_PROGRESS_LEAD_FACTOR);

  if ((state === 'paused' || state === 'idle') && ownerKey && ownerKey !== playerKey) {
    return;
  }

  if (state === 'playing' || (state === 'paused' && progressValue > 0)) {
    target.dataset.audioFeedbackOwner = playerKey;
  }

  if (state === 'idle') {
    delete target.dataset.audioFeedbackOwner;
  }

  target.dataset.audioState = state;
  target.style.setProperty('--pm-audio-linked-progress', `${progressValue.toFixed(3)}%`);
}

function syncMiniPlayer(player, audio, toggle, icon, progress, timeLabel, playLabel, pauseLabel, forcedState = '') {
  const duration = getKnownDuration(audio);
  const currentTime = Number.isFinite(audio.currentTime) ? audio.currentTime : 0;
  const playbackState = getPlaybackState(audio, forcedState);
  const isPlaying = playbackState === 'playing';
  const nextLabel = isPlaying ? pauseLabel : playLabel;

  toggle.setAttribute('aria-label', nextLabel);
  toggle.setAttribute('title', nextLabel);
  icon.textContent = isPlaying ? 'pause' : 'play_arrow';

  if (duration > 0) {
    progress.disabled = false;
    progress.value = String(Math.min(1000, Math.max(0, Math.round((currentTime / duration) * 1000))));
    timeLabel.textContent = `${formatClock(currentTime)} / ${formatClock(duration)}`;
  } else {
    progress.disabled = true;
    progress.value = '0';
    timeLabel.textContent = '0:00 / 0:00';
  }

  syncLinkedAudioFeedback(player, audio, playbackState);
}

function pauseOtherTeachingPlayers(currentAudio) {
  document.querySelectorAll('.pm-teaching-mini-player__audio').forEach((audioElement) => {
    if (!(audioElement instanceof HTMLAudioElement) || audioElement === currentAudio) {
      return;
    }
    if (audioElement.paused) {
      return;
    }

    audioElement.dataset.pauseReason = 'superseded';
    audioElement.pause();
  });
}

export function initTeachingMiniPlayers() {
  const players = Array.from(document.querySelectorAll('[data-teaching-mini-player]'));

  for (const player of players) {
    if (!(player instanceof HTMLElement) || player.dataset.teachingMiniPlayerReady === 'true') {
      continue;
    }

    const audio = player.querySelector('.pm-teaching-mini-player__audio');
    const toggle = player.querySelector('[data-teaching-mini-player-toggle]');
    const icon = player.querySelector('[data-teaching-mini-player-icon]');
    const progress = player.querySelector('[data-teaching-mini-player-progress]');
    const timeLabel = player.querySelector('[data-teaching-mini-player-time]');
    if (!(audio instanceof HTMLAudioElement) || !(toggle instanceof HTMLButtonElement) || !(icon instanceof HTMLElement) || !(progress instanceof HTMLInputElement) || !(timeLabel instanceof HTMLElement)) {
      continue;
    }

    const playLabel = player.dataset.playLabel || 'Play audio';
    const pauseLabel = player.dataset.pauseLabel || 'Pause audio';
    const sync = (forcedState = '') => syncMiniPlayer(player, audio, toggle, icon, progress, timeLabel, playLabel, pauseLabel, forcedState);
    let feedbackFrameId = 0;

    const stopFeedbackLoop = () => {
      if (feedbackFrameId) {
        cancelAnimationFrame(feedbackFrameId);
        feedbackFrameId = 0;
      }
    };

    const startFeedbackLoop = () => {
      if (feedbackFrameId || prefersReducedMotion()) {
        return;
      }

      const tick = () => {
        if (audio.paused || audio.ended) {
          feedbackFrameId = 0;
          return;
        }

        syncLinkedAudioFeedback(player, audio, 'playing');
        feedbackFrameId = requestAnimationFrame(tick);
      };

      feedbackFrameId = requestAnimationFrame(tick);
    };

    if (audio.preload !== 'metadata') {
      audio.preload = 'metadata';
    }

    toggle.addEventListener('click', async () => {
      if (!audio.paused) {
        audio.pause();
        sync();
        return;
      }

      pauseOtherTeachingPlayers(audio);
      try {
        await audio.play();
      } catch {
        sync();
      }
    });

    progress.addEventListener('input', () => {
      const duration = Number.isFinite(audio.duration) ? audio.duration : 0;
      if (duration <= 0) {
        return;
      }
      audio.currentTime = (Number(progress.value || '0') / 1000) * duration;
      sync();
    });

    audio.addEventListener('loadedmetadata', sync);
    audio.addEventListener('durationchange', sync);
    audio.addEventListener('timeupdate', sync);
    audio.addEventListener('play', () => {
      pauseOtherTeachingPlayers(audio);
      sync();
      startFeedbackLoop();
    });
    audio.addEventListener('pause', () => {
      stopFeedbackLoop();
      const pauseReason = audio.dataset.pauseReason || '';
      delete audio.dataset.pauseReason;
      sync(pauseReason === 'superseded' || pauseReason === 'ended' ? 'idle' : '');
    });
    audio.addEventListener('ended', () => {
      stopFeedbackLoop();
      audio.dataset.pauseReason = 'ended';
      if (Number.isFinite(audio.duration) && audio.duration > 0) {
        audio.currentTime = 0;
      }
      sync('idle');
    });

    player.dataset.teachingMiniPlayerReady = 'true';
    player.classList.add('is-ready');

    if (audio.readyState < 1) {
      audio.load();
    }

    sync();

    if (!audio.paused && !audio.ended) {
      startFeedbackLoop();
    }
  }
}