/**
 * UI State Manager
 *
 * Manages showing/hiding sections and updating UI state.
 * Single responsibility: Section visibility and state-driven UI updates.
 */
export class UIStateManager {
  constructor(state, audioPlayerLoader) {
    this.state = state;
    this.loadAudioPlayer = audioPlayerLoader;
  }

  /**
   * Update progress step indicator based on current step
   * @param {string} currentStep - Current step: 'upload', 'transcribe', or 'results'
   */
  updateProgressSteps(currentStep) {
    const steps = ['upload', 'transcribe', 'results'];
    const currentIndex = steps.indexOf(currentStep);

    steps.forEach((step, index) => {
      const stepElement = document.querySelector(`.progress-steps__item[data-step="${step}"]`);
      if (!stepElement) return;

      // Reset classes
      stepElement.classList.remove('progress-steps__item--active', 'progress-steps__item--completed');

      if (index < currentIndex) {
        // Previous steps are completed
        stepElement.classList.add('progress-steps__item--completed');
      } else if (index === currentIndex) {
        // Current step is active
        stepElement.classList.add('progress-steps__item--active');
      }
      // Future steps remain default (inactive)
    });
  }

  /**
   * Show transcription section after upload
   */
  showTranscriptionSection() {
    this.state.currentStep = 'transcribe';

    // Update progress indicator
    this.updateProgressSteps('transcribe');

    // Hide upload, show transcribe
    document.getElementById('upload-section').classList.add('hidden');
    document.getElementById('transcribe-section').classList.remove('hidden');

    // Populate transcript
    const editor = document.getElementById('transcript-editor');
    editor.value = this.state.transcription;

    // Apply RTL/LTR direction to the transcript editor based on source language
    if (editor) {
      const isRTL = this.isRTL(this.state.sourceLanguage);
      editor.style.direction = isRTL ? 'rtl' : 'ltr';
      editor.style.textAlign = isRTL ? 'right' : 'left';
    }

    // Update character count
    this.updateCharCount();

    // Set source language
    const sourceLangSelect = document.getElementById('source-language');
    if (sourceLangSelect) {
      sourceLangSelect.value = this.state.sourceLanguage;
    }

    // Load audio player for original audio
    if (this.state.originalAudioUrl) {
      this.state.originalPlayer = this.loadAudioPlayer('original-audio-player', this.state.originalAudioUrl);
    }
  }

  /**
   * Update character count display
   */
  updateCharCount() {
    const editor = document.getElementById('transcript-editor');
    const charCount = document.getElementById('char-count');

    if (!editor || !charCount) return;

    const count = editor.value.length;
    const max = 50000;

    charCount.textContent = `${count.toLocaleString()} / ${max.toLocaleString()}`;

    // Update styling based on count
    charCount.classList.remove('transcript-box__char-count--error', 'transcript-box__char-count--warning');

    if (count > max) {
      charCount.classList.add('transcript-box__char-count--error');
    } else if (count > max * 0.9) {
      charCount.classList.add('transcript-box__char-count--warning');
    }
  }

  /**
   * RTL (Right-to-Left) languages for text direction
   */
  static RTL_LANGUAGES = ['hebrew', 'arabic', 'persian', 'urdu'];

  /**
   * Check if a language is RTL
   * @param {string} language - Language name
   * @returns {boolean} - True if RTL language
   */
  isRTL(language) {
    return UIStateManager.RTL_LANGUAGES.includes(language?.toLowerCase());
  }

  /**
   * Update transcript editor text direction based on source language
   * Call this when the source language changes
   */
  updateEditorDirection() {
    const editor = document.getElementById('transcript-editor');
    if (editor) {
      const isRTL = this.isRTL(this.state.sourceLanguage);
      editor.style.direction = isRTL ? 'rtl' : 'ltr';
      editor.style.textAlign = isRTL ? 'right' : 'left';
    }
  }

  /**
   * Show results section after translation/TTS
   * @param {Object} audioReactiveUI - AudioReactiveUI instance to wire up
   */
  showResults(audioReactiveUI) {
    this.state.currentStep = 'results';

    // Update progress indicator
    this.updateProgressSteps('results');

    // Hide transcribe, show results
    document.getElementById('transcribe-section').classList.add('hidden');
    document.getElementById('results-section').classList.remove('hidden');

    // Update titles with language names
    const originalTitle = document.getElementById('original-title');
    const generatedTitle = document.getElementById('generated-title');

    if (originalTitle) {
      originalTitle.textContent = `Original Audio (${this.capitalize(this.state.sourceLanguage)})`;
    }

    if (generatedTitle) {
      generatedTitle.textContent = `Generated Audio (${this.capitalize(this.state.targetLanguage)})`;
    }

    // Display transcripts with proper text direction
    const originalTranscript = document.getElementById('original-transcript');
    const translatedTranscript = document.getElementById('translated-transcript');

    if (originalTranscript) {
      originalTranscript.textContent = this.state.transcription;
      // Apply RTL/LTR class to parent container
      const originalContainer = originalTranscript.closest('.transcript-display');
      if (originalContainer) {
        originalContainer.classList.remove('transcript-display--rtl', 'transcript-display--ltr');
        originalContainer.classList.add(
          this.isRTL(this.state.sourceLanguage) ? 'transcript-display--rtl' : 'transcript-display--ltr'
        );
      }
    }

    if (translatedTranscript) {
      translatedTranscript.textContent = this.state.translation;
      // Apply RTL/LTR class to parent container
      const translatedContainer = translatedTranscript.closest('.transcript-display');
      if (translatedContainer) {
        translatedContainer.classList.remove('transcript-display--rtl', 'transcript-display--ltr');
        translatedContainer.classList.add(
          this.isRTL(this.state.targetLanguage) ? 'transcript-display--rtl' : 'transcript-display--ltr'
        );
      }
    }

    // Load audio players
    if (this.state.originalAudioUrl) {
      this.state.originalPlayerResult = this.loadAudioPlayer('original-player-result', this.state.originalAudioUrl);
    }

    if (this.state.generatedAudioUrl) {
      this.state.generatedPlayer = this.loadAudioPlayer('generated-player', this.state.generatedAudioUrl);
    }

    // Wire up AudioReactiveUI to audio playback events
    const audioPlayers = [this.state.originalPlayerResult, this.state.generatedPlayer].filter(p => p);

    audioPlayers.forEach(player => {
      const audioElement = player.audio;
      if (audioElement && audioReactiveUI) {
        audioElement.addEventListener('play', () => {
          audioReactiveUI.start(audioElement);
        });
        audioElement.addEventListener('pause', () => {
          audioReactiveUI.stop();
        });
        audioElement.addEventListener('ended', () => {
          audioReactiveUI.stop();
        });
      }
    });
  }

  /**
   * Reset UI to initial state
   */
  reset() {
    // Update progress indicator to first step
    this.updateProgressSteps('upload');

    // Show upload section, hide others
    document.getElementById('upload-section').classList.remove('hidden');
    document.getElementById('transcribe-section').classList.add('hidden');
    document.getElementById('results-section').classList.add('hidden');

    // Clear form fields
    const transcriptEditor = document.getElementById('transcript-editor');
    if (transcriptEditor) {
      transcriptEditor.value = '';
    }

    this.updateCharCount();
  }

  /**
   * Capitalize first letter of string
   * @param {string} str - String to capitalize
   * @returns {string} - Capitalized string
   */
  capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
}
