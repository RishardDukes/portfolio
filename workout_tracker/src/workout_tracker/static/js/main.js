document.addEventListener('DOMContentLoaded', () => {
  const selectors = {
    interactive: 'button, .btn, input[type="submit"], input[type="button"], [role="button"], .nav-link',
    spaLink: 'a[data-spa-nav="true"]'
  };

  const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
  const audioContext = AudioContextCtor ? new AudioContextCtor() : null;

  const appAudio = window.__wipAudio || {
    started: false,
    bgMusic: null,
    isMuted: localStorage.getItem('wipMusicMuted') === 'true',
    currentTrack: localStorage.getItem('wipMusicTrack') || 'Wii.mp3'
  };
  window.__wipAudio = appAudio;

  const dedupeAudioToggles = () => {
    const toggles = Array.from(document.querySelectorAll('[data-audio-toggle="true"]'));
    if (toggles.length <= 1) {
      return toggles[0] || null;
    }

    // Keep the first toggle in DOM order and remove accidental duplicates.
    toggles.slice(1).forEach(toggle => toggle.remove());
    return toggles[0];
  };

  const buildTrackUrl = trackName => `/static/sounds/${encodeURIComponent(trackName)}`;

  const getTrackPickers = () => Array.from(document.querySelectorAll('[data-music-picker="true"]'));

  const ensureBgMusic = () => {
    const targetSrc = buildTrackUrl(appAudio.currentTrack);

    if (!appAudio.bgMusic) {
      appAudio.bgMusic = new Audio(targetSrc);
      appAudio.bgMusic.loop = true;
      appAudio.bgMusic.volume = 0.1;
      return;
    }

    const currentSrc = appAudio.bgMusic.getAttribute('src') || '';
    if (currentSrc !== targetSrc) {
      appAudio.bgMusic.pause();
      appAudio.bgMusic = new Audio(targetSrc);
      appAudio.bgMusic.loop = true;
      appAudio.bgMusic.volume = 0.1;
      appAudio.started = false;
    }
  };

  const updateToggleLabel = () => {
    const toggle = dedupeAudioToggles();
    if (!toggle) {
      return;
    }
    toggle.textContent = appAudio.isMuted ? 'Music: Off' : 'Music: On';
    toggle.setAttribute('aria-pressed', String(!appAudio.isMuted));
  };

  const startMusicIfNeeded = () => {
    if (appAudio.started || appAudio.isMuted) {
      return;
    }

    if (audioContext && audioContext.state === 'suspended') {
      audioContext.resume().catch(() => {});
    }

    ensureBgMusic();

    appAudio.bgMusic.play().then(() => {
      appAudio.started = true;
    }).catch(() => {
      appAudio.started = false;
    });
  };

  const stopMusic = () => {
    if (!appAudio.bgMusic) {
      return;
    }

    appAudio.bgMusic.pause();
    appAudio.started = false;
  };

  const toggleMusic = () => {
    appAudio.isMuted = !appAudio.isMuted;
    localStorage.setItem('wipMusicMuted', String(appAudio.isMuted));

    if (appAudio.isMuted) {
      stopMusic();
    } else {
      startMusicIfNeeded();
    }
    updateToggleLabel();
  };

  const setTrack = trackName => {
    if (!trackName || trackName === appAudio.currentTrack) {
      return;
    }

    const wasPlaying = appAudio.started && !appAudio.isMuted;
    appAudio.currentTrack = trackName;
    localStorage.setItem('wipMusicTrack', trackName);
    appAudio.started = false;

    ensureBgMusic();
    if (wasPlaying) {
      startMusicIfNeeded();
    }
  };

  const syncPickerSelection = () => {
    getTrackPickers().forEach(picker => {
      if (picker.value !== appAudio.currentTrack) {
        picker.value = appAudio.currentTrack;
      }
    });
  };

  const populateTrackPicker = async () => {
    const pickers = getTrackPickers();
    if (!pickers.length) {
      return;
    }

    try {
      const response = await fetch('/api/music/tracks', { credentials: 'same-origin' });
      if (!response.ok) {
        throw new Error('Failed to load tracks');
      }

      const tracks = await response.json();
      if (!Array.isArray(tracks) || tracks.length === 0) {
        pickers.forEach(picker => {
          picker.innerHTML = '<option value="">No tracks found</option>';
          picker.disabled = true;
        });
        return;
      }

      if (!tracks.includes(appAudio.currentTrack)) {
        appAudio.currentTrack = tracks[0];
        localStorage.setItem('wipMusicTrack', appAudio.currentTrack);
      }

      const optionsMarkup = tracks
        .map(track => `<option value="${track}">${track.replace(/\.[^/.]+$/, '')}</option>`)
        .join('');

      pickers.forEach(picker => {
        picker.innerHTML = optionsMarkup;
        picker.value = appAudio.currentTrack;
        picker.disabled = false;
        picker.onchange = () => {
          setTrack(picker.value);
          syncPickerSelection();
          if (!appAudio.isMuted) {
            startMusicIfNeeded();
          }
        };
      });
    } catch {
      pickers.forEach(picker => {
        picker.innerHTML = '<option value="">Tracks unavailable</option>';
        picker.disabled = true;
      });
    }
  };

  const playFuturisticClick = () => {
    if (!audioContext) {
      return;
    }

    if (audioContext.state === 'suspended') {
      audioContext.resume().catch(() => {});
    }

    const now = audioContext.currentTime;
    const masterGain = audioContext.createGain();
    masterGain.gain.setValueAtTime(0.0001, now);
    masterGain.gain.exponentialRampToValueAtTime(0.05, now + 0.012);
    masterGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.15);
    masterGain.connect(audioContext.destination);

    const oscA = audioContext.createOscillator();
    oscA.type = 'triangle';
    oscA.frequency.setValueAtTime(820, now);
    oscA.frequency.exponentialRampToValueAtTime(1320, now + 0.055);
    oscA.connect(masterGain);

    const oscB = audioContext.createOscillator();
    oscB.type = 'sine';
    oscB.frequency.setValueAtTime(1640, now);
    oscB.frequency.exponentialRampToValueAtTime(920, now + 0.07);
    oscB.connect(masterGain);

    oscA.start(now);
    oscB.start(now);
    oscA.stop(now + 0.16);
    oscB.stop(now + 0.1);
  };

  const executeInlineScripts = container => {
    container.querySelectorAll('script').forEach(oldScript => {
      const replacement = document.createElement('script');
      Array.from(oldScript.attributes).forEach(attr => replacement.setAttribute(attr.name, attr.value));
      if (oldScript.src) {
        replacement.textContent = oldScript.textContent;
      } else {
        replacement.textContent = `(function () {\n${oldScript.textContent}\n})();`;
      }
      oldScript.replaceWith(replacement);
    });
  };

  const loadHeadScripts = async doc => {
    const scripts = Array.from(doc.querySelectorAll('head script[src]')).map(script => script.getAttribute('src')).filter(Boolean);
    for (const src of scripts) {
      if (document.querySelector(`script[src="${src}"]`)) {
        continue;
      }

      await new Promise(resolve => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = () => resolve();
        script.onerror = () => resolve();
        document.head.appendChild(script);
      });
    }
  };

  const shouldHandleSpa = (link, event) => {
    if (!link || !link.matches(selectors.spaLink)) {
      return false;
    }

    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return false;
    }

    if (link.target && link.target !== '_self') {
      return false;
    }

    const url = new URL(link.href, window.location.origin);
    if (url.origin !== window.location.origin) {
      return false;
    }

    return true;
  };

  const swapPage = async (url, pushHistory) => {
    const response = await fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    });

    if (!response.ok) {
      window.location.href = url;
      return;
    }

    const html = await response.text();
    const parser = new DOMParser();
    const nextDoc = parser.parseFromString(html, 'text/html');
    const incomingMain = nextDoc.querySelector('#page-wrap');
    const currentMain = document.querySelector('#page-wrap');

    if (!incomingMain || !currentMain) {
      window.location.href = url;
      return;
    }

    await loadHeadScripts(nextDoc);

    currentMain.innerHTML = incomingMain.innerHTML;
    document.title = nextDoc.title || document.title;

    if (pushHistory) {
      window.history.pushState({ spa: true }, '', url);
    }

    executeInlineScripts(currentMain);
    dedupeAudioToggles();
    updateToggleLabel();
    populateTrackPicker();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  document.addEventListener('click', event => {
    const link = event.target instanceof Element ? event.target.closest('a') : null;
    if (!shouldHandleSpa(link, event)) {
      return;
    }

    event.preventDefault();
    swapPage(link.href, true).catch(() => {
      window.location.href = link.href;
    });
  });

  window.addEventListener('popstate', () => {
    swapPage(window.location.href, false).catch(() => {
      window.location.reload();
    });
  });

  document.addEventListener('pointerdown', event => {
    if (!(event.target instanceof Element)) {
      return;
    }

    const audioToggle = event.target.closest('[data-audio-toggle="true"]');
    if (audioToggle) {
      playFuturisticClick();
      toggleMusic();
      return;
    }

    const control = event.target.closest(selectors.interactive);
    if (control && !control.matches(':disabled, [aria-disabled="true"]')) {
      playFuturisticClick();
      startMusicIfNeeded();
    }
  });

  document.addEventListener('keydown', event => {
    const isActivateKey = event.key === 'Enter' || event.key === ' ';
    if (!isActivateKey || !(event.target instanceof Element)) {
      return;
    }

    const control = event.target.closest(selectors.interactive);
    if (control && !control.matches(':disabled, [aria-disabled="true"]')) {
      playFuturisticClick();
      startMusicIfNeeded();
    }
  });

  document.querySelectorAll('a[href="#"]').forEach(link => {
    link.addEventListener('click', event => event.preventDefault());
  });

  dedupeAudioToggles();
  updateToggleLabel();
  populateTrackPicker();

  const hasMusicToggle = Boolean(document.querySelector('[data-audio-toggle="true"]'));
  if (hasMusicToggle && !appAudio.isMuted) {
    startMusicIfNeeded();
  }

  window.addEventListener('focus', () => {
    if (hasMusicToggle && !appAudio.isMuted) {
      startMusicIfNeeded();
    }
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && hasMusicToggle && !appAudio.isMuted) {
      startMusicIfNeeded();
    }
  });
});
