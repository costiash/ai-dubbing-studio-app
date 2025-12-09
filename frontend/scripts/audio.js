/**
 * Audio Player - AI Dubbing Studio
 *
 * Custom audio player with playback controls
 * Supports play/pause, seek, playback speed, and keyboard shortcuts
 */

/**
 * Format seconds to MM:SS
 * @param {number} seconds - Seconds to format
 * @returns {string} - Formatted time string
 */
function formatTime(seconds) {
  if (isNaN(seconds) || seconds === Infinity) {
    return '0:00';
  }

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Audio Player class
 */
export class AudioPlayer {
  constructor(containerId, audioUrl) {
    this.container = document.getElementById(containerId);
    this.audioUrl = audioUrl;
    this.audio = null;
    this.isPlaying = false;
    this.playbackSpeed = 1.0;

    // UI elements
    this.playBtn = null;
    this.progressBar = null;
    this.progressFill = null;
    this.progressHandle = null;
    this.timeCurrent = null;
    this.timeTotal = null;
    this.speedBtns = [];

    // Store bound event handlers for proper cleanup
    this.boundHandlers = {
      keydown: null,
      play: null,
      pause: null,
      timeupdate: null,
      loadedmetadata: null,
      ended: null,
    };

    if (this.container) {
      this.init();
    } else {
      console.error(`Audio player container not found: ${containerId}`);
    }
  }

  /**
   * Initialize audio player
   */
  init() {
    this.audio = new Audio(this.audioUrl);
    this.buildUI();
    this.setupEventListeners();
  }

  /**
   * Build player UI
   */
  buildUI() {
    this.container.innerHTML = `
      <button class="audio-player__control" aria-label="Play audio">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M8 5v14l11-7z"/>
        </svg>
      </button>

      <div class="audio-player__progress-container">
        <div class="audio-player__progress" role="slider" aria-label="Seek audio" tabindex="0">
          <div class="audio-player__progress-fill"></div>
          <div class="audio-player__progress-handle"></div>
        </div>
        <div class="audio-player__time">
          <span class="audio-player__time-current">0:00</span>
          <span class="audio-player__time-total">0:00</span>
        </div>
      </div>

      <div class="audio-player__speed">
        <button class="audio-player__speed-btn" data-speed="0.75" aria-label="Playback speed 0.75x">0.75x</button>
        <button class="audio-player__speed-btn audio-player__speed-btn--active" data-speed="1.0" aria-label="Playback speed 1x">1.0x</button>
        <button class="audio-player__speed-btn" data-speed="1.25" aria-label="Playback speed 1.25x">1.25x</button>
        <button class="audio-player__speed-btn" data-speed="1.5" aria-label="Playback speed 1.5x">1.5x</button>
      </div>
    `;

    // Store references to UI elements
    this.playBtn = this.container.querySelector('.audio-player__control');
    this.progressBar = this.container.querySelector('.audio-player__progress');
    this.progressFill = this.container.querySelector('.audio-player__progress-fill');
    this.progressHandle = this.container.querySelector('.audio-player__progress-handle');
    this.timeCurrent = this.container.querySelector('.audio-player__time-current');
    this.timeTotal = this.container.querySelector('.audio-player__time-total');
    this.speedBtns = this.container.querySelectorAll('.audio-player__speed-btn');
  }

  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Play/Pause button
    this.playBtn.addEventListener('click', () => this.togglePlay());

    // Store bound handlers for proper cleanup
    this.boundHandlers.play = () => this.onPlay();
    this.boundHandlers.pause = () => this.onPause();
    this.boundHandlers.timeupdate = () => this.onTimeUpdate();
    this.boundHandlers.loadedmetadata = () => this.onLoadedMetadata();
    this.boundHandlers.ended = () => this.onEnded();

    // Audio events
    this.audio.addEventListener('play', this.boundHandlers.play);
    this.audio.addEventListener('pause', this.boundHandlers.pause);
    this.audio.addEventListener('timeupdate', this.boundHandlers.timeupdate);
    this.audio.addEventListener('loadedmetadata', this.boundHandlers.loadedmetadata);
    this.audio.addEventListener('ended', this.boundHandlers.ended);

    // Seek on progress bar click
    this.progressBar.addEventListener('click', (e) => this.seek(e));

    // Playback speed buttons
    this.speedBtns.forEach(btn => {
      btn.addEventListener('click', () => this.setSpeed(parseFloat(btn.dataset.speed)));
    });

    // Keyboard shortcuts (only when not typing in inputs)
    // Store bound handler to enable proper removal
    this.boundHandlers.keydown = (e) => {
      // Ignore if user is typing in an input/textarea
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      if (e.key === ' ') {
        e.preventDefault();
        this.togglePlay();
      } else if (e.key === 'j' || e.key === 'ArrowLeft') {
        e.preventDefault();
        this.skip(-10);
      } else if (e.key === 'l' || e.key === 'ArrowRight') {
        e.preventDefault();
        this.skip(10);
      }
    };
    document.addEventListener('keydown', this.boundHandlers.keydown);
  }

  /**
   * Toggle play/pause
   */
  togglePlay() {
    if (this.isPlaying) {
      this.audio.pause();
    } else {
      this.audio.play();
    }
  }

  /**
   * Play event handler
   */
  onPlay() {
    this.isPlaying = true;
    this.playBtn.setAttribute('aria-label', 'Pause audio');

    // Update icon to pause
    this.playBtn.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 4h4v16H6zm8 0h4v16h-4z"/>
      </svg>
    `;
  }

  /**
   * Pause event handler
   */
  onPause() {
    this.isPlaying = false;
    this.playBtn.setAttribute('aria-label', 'Play audio');

    // Update icon to play
    this.playBtn.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M8 5v14l11-7z"/>
      </svg>
    `;
  }

  /**
   * Time update event handler
   */
  onTimeUpdate() {
    // Guard against invalid duration values
    if (!isFinite(this.audio.duration) || this.audio.duration === 0) {
      return;
    }

    const progress = (this.audio.currentTime / this.audio.duration) * 100;
    const clampedProgress = Math.max(0, Math.min(100, progress));

    this.progressFill.style.width = `${clampedProgress}%`;
    this.progressHandle.style.left = `${clampedProgress}%`;
    this.timeCurrent.textContent = formatTime(this.audio.currentTime);

    // Update ARIA attributes
    this.progressBar.setAttribute('aria-valuenow', Math.floor(clampedProgress));
    this.progressBar.setAttribute('aria-valuetext',
      `${formatTime(this.audio.currentTime)} of ${formatTime(this.audio.duration)}`
    );
  }

  /**
   * Loaded metadata event handler
   */
  onLoadedMetadata() {
    this.timeTotal.textContent = formatTime(this.audio.duration);

    // Set up ARIA attributes
    this.progressBar.setAttribute('aria-valuemin', '0');
    this.progressBar.setAttribute('aria-valuemax', '100');
    this.progressBar.setAttribute('aria-valuenow', '0');
  }

  /**
   * Ended event handler
   */
  onEnded() {
    this.isPlaying = false;
    this.audio.currentTime = 0;

    // CRITICAL: Update UI state to reflect stopped playback
    // Call onPause to update button icon and ARIA label
    this.onPause();
  }

  /**
   * Seek to position
   * @param {Event} e - Click event
   */
  seek(e) {
    const rect = this.progressBar.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percent = Math.max(0, Math.min(1, clickX / rect.width));

    this.audio.currentTime = percent * this.audio.duration;
  }

  /**
   * Skip forward or backward
   * @param {number} seconds - Seconds to skip (negative for backward)
   */
  skip(seconds) {
    this.audio.currentTime = Math.max(
      0,
      Math.min(this.audio.duration, this.audio.currentTime + seconds)
    );
  }

  /**
   * Set playback speed
   * @param {number} speed - Playback rate
   */
  setSpeed(speed) {
    this.audio.playbackRate = speed;
    this.playbackSpeed = speed;

    // Update active state on buttons
    this.speedBtns.forEach(btn => {
      if (parseFloat(btn.dataset.speed) === speed) {
        btn.classList.add('audio-player__speed-btn--active');
      } else {
        btn.classList.remove('audio-player__speed-btn--active');
      }
    });
  }

  /**
   * Clean up resources
   */
  destroy() {
    // CRITICAL: Remove all event listeners to prevent memory leaks
    if (this.audio) {
      // Remove audio event listeners
      if (this.boundHandlers.play) {
        this.audio.removeEventListener('play', this.boundHandlers.play);
      }
      if (this.boundHandlers.pause) {
        this.audio.removeEventListener('pause', this.boundHandlers.pause);
      }
      if (this.boundHandlers.timeupdate) {
        this.audio.removeEventListener('timeupdate', this.boundHandlers.timeupdate);
      }
      if (this.boundHandlers.loadedmetadata) {
        this.audio.removeEventListener('loadedmetadata', this.boundHandlers.loadedmetadata);
      }
      if (this.boundHandlers.ended) {
        this.audio.removeEventListener('ended', this.boundHandlers.ended);
      }

      // Stop playback and clean up audio element
      this.audio.pause();
      this.audio.src = '';
      this.audio = null;
    }

    // Remove global keydown listener
    if (this.boundHandlers.keydown) {
      document.removeEventListener('keydown', this.boundHandlers.keydown);
      this.boundHandlers.keydown = null;
    }

    // Clear all bound handlers
    this.boundHandlers = {
      keydown: null,
      play: null,
      pause: null,
      timeupdate: null,
      loadedmetadata: null,
      ended: null,
    };
  }
}

/**
 * Load and initialize audio player
 * @param {string} containerId - Container element ID
 * @param {string} audioUrl - Audio file URL
 * @returns {AudioPlayer} - Audio player instance
 */
export function loadAudioPlayer(containerId, audioUrl) {
  return new AudioPlayer(containerId, audioUrl);
}
