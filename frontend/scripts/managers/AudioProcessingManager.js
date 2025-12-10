/**
 * Audio Processing Manager
 *
 * Orchestrates translation and TTS generation workflow.
 * Single responsibility: Translate → Generate TTS → Show results.
 */
import { lockUI, unlockUI } from '../utils/ui-lock.js';

export class AudioProcessingManager {
  constructor(apiClient, uiStateManager, uiFeedbackManager, state, particleSystem, sessionManager) {
    this.apiClient = apiClient;
    this.uiStateManager = uiStateManager;
    this.uiFeedbackManager = uiFeedbackManager;
    this.state = state;
    this.particleSystem = particleSystem;
    this.sessionManager = sessionManager;
    this.isProcessing = false;
  }

  /**
   * Handle translation and TTS generation
   * @param {Object} audioReactiveUI - AudioReactiveUI instance to wire up in results
   */
  async handleTranslate(audioReactiveUI) {
    // CRITICAL: Prevent concurrent processing requests (race condition guard)
    if (this.isProcessing) {
      console.warn('Processing already in progress, ignoring duplicate request');
      this.uiFeedbackManager.showError('Processing already in progress. Please wait.');
      return;
    }

    const editor = document.getElementById('transcript-editor');
    const text = editor?.value || this.state.transcription;

    if (!text.trim()) {
      this.uiFeedbackManager.showError('No text to translate. Please enter or upload audio first.');
      return;
    }

    if (text.length > 50000) {
      this.uiFeedbackManager.showError('Text is too long. Maximum length is 50,000 characters.');
      return;
    }

    // Get language selections
    const sourceLangSelect = document.getElementById('source-language');
    const targetLangSelect = document.getElementById('target-language');

    this.state.sourceLanguage = sourceLangSelect?.value || this.state.sourceLanguage;
    this.state.targetLanguage = targetLangSelect?.value || this.state.targetLanguage;

    console.log(`Translating from ${this.state.sourceLanguage} to ${this.state.targetLanguage}...`);

    // Set guard flag
    this.isProcessing = true;
    // Lock UI to prevent interaction during translation and TTS
    lockUI('translating and generating audio');

    try {
      // Step 1: Translate
      this.uiFeedbackManager.showLoading('Translating text...');

      // Start particle system during processing
      if (this.particleSystem) {
        this.particleSystem.start();
      }

      const translateResult = await this.apiClient.translateText(
        text,
        this.capitalize(this.state.sourceLanguage),
        this.capitalize(this.state.targetLanguage)
      );

      this.state.translation = translateResult.translated_text;

      console.log('Translation complete:', this.state.translation.substring(0, 100) + '...');

      // Save to session
      this.sessionManager.saveState('translation', this.state.translation);

      // Step 2: Generate TTS
      this.uiFeedbackManager.showLoading('Generating speech...');

      const audioBlob = await this.apiClient.generateTTS(
        this.state.translation,
        this.state.voice,
        this.state.model,
        this.state.instructions || null
      );

      this.state.generatedAudioBlob = audioBlob;
      this.state.generatedAudioUrl = URL.createObjectURL(audioBlob);

      console.log('TTS generation complete');

      // Show results
      this.uiStateManager.showResults(audioReactiveUI);

      this.uiFeedbackManager.hideLoading();

      // Stop particle system after processing completes
      if (this.particleSystem) {
        this.particleSystem.stop();
      }

    } catch (error) {
      console.error('Processing failed:', error);
      this.uiFeedbackManager.hideLoading();
      this.uiFeedbackManager.showError(`Processing failed: ${error.message}`);

      // Stop particle system on error
      if (this.particleSystem) {
        this.particleSystem.stop();
      }
    } finally {
      // Always reset guard flag and unlock UI
      this.isProcessing = false;
      unlockUI();
    }
  }

  /**
   * Handle audio download
   */
  handleDownload() {
    if (!this.state.generatedAudioBlob) {
      this.uiFeedbackManager.showError('No audio to download');
      return;
    }

    const url = this.state.generatedAudioUrl;
    const a = document.createElement('a');
    a.href = url;
    a.download = `dubbed_audio_${this.state.targetLanguage}_${Date.now()}.mp3`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    console.log('Audio downloaded');
  }

  /**
   * Reset processing state
   */
  reset() {
    this.isProcessing = false;
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
