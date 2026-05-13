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

function syncMiniPlayer(player, audio, toggle, icon, progress, timeLabel, playLabel, pauseLabel) {
  const duration = getKnownDuration(audio);
  const currentTime = Number.isFinite(audio.currentTime) ? audio.currentTime : 0;
  const isPlaying = !audio.paused;
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
}

function pauseOtherTeachingPlayers(currentAudio) {
  document.querySelectorAll('.pm-teaching-mini-player__audio').forEach((audioElement) => {
    if (!(audioElement instanceof HTMLAudioElement) || audioElement === currentAudio) {
      return;
    }
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
    const sync = () => syncMiniPlayer(player, audio, toggle, icon, progress, timeLabel, playLabel, pauseLabel);

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
    });
    audio.addEventListener('pause', sync);
    audio.addEventListener('ended', sync);

    player.dataset.teachingMiniPlayerReady = 'true';
    player.classList.add('is-ready');

    if (audio.readyState < 1) {
      audio.load();
    }

    sync();
  }
}