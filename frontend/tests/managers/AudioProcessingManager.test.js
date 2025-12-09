import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AudioProcessingManager } from '../../scripts/managers/AudioProcessingManager.js';
import * as uiLock from '../../scripts/utils/ui-lock.js';

// Mock lockUI/unlockUI
vi.mock('../../scripts/utils/ui-lock.js', () => ({
  lockUI: vi.fn(),
  unlockUI: vi.fn()
}));

describe('AudioProcessingManager', () => {
  let manager;
  let mockApiClient;
  let mockUIStateManager;
  let mockUIFeedbackManager;
  let mockState;
  let mockParticleSystem;
  let mockSessionManager;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();

    // Set up DOM
    document.body.innerHTML = `
      <textarea id="transcript-editor">Test transcript</textarea>
      <select id="source-language">
        <option value="hebrew" selected>Hebrew</option>
      </select>
      <select id="target-language">
        <option value="english" selected>English</option>
      </select>
    `;

    // Create mocks
    mockApiClient = {
      translateText: vi.fn(),
      generateTTS: vi.fn()
    };

    mockUIStateManager = {
      showResults: vi.fn()
    };

    mockUIFeedbackManager = {
      showLoading: vi.fn(),
      hideLoading: vi.fn(),
      showError: vi.fn()
    };

    mockState = {
      transcription: 'Test transcript',
      translation: null,
      sourceLanguage: 'hebrew',
      targetLanguage: 'english',
      voice: 'alloy',
      model: 'tts-1',
      generatedAudioBlob: null,
      generatedAudioUrl: null
    };

    mockParticleSystem = {
      start: vi.fn(),
      stop: vi.fn()
    };

    mockSessionManager = {
      saveState: vi.fn()
    };

    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');

    // Create manager instance
    manager = new AudioProcessingManager(
      mockApiClient,
      mockUIStateManager,
      mockUIFeedbackManager,
      mockState,
      mockParticleSystem,
      mockSessionManager
    );
  });

  describe('Constructor', () => {
    it('should initialize with all dependencies', () => {
      expect(manager.apiClient).toBe(mockApiClient);
      expect(manager.uiStateManager).toBe(mockUIStateManager);
      expect(manager.uiFeedbackManager).toBe(mockUIFeedbackManager);
      expect(manager.state).toBe(mockState);
      expect(manager.particleSystem).toBe(mockParticleSystem);
      expect(manager.sessionManager).toBe(mockSessionManager);
    });

    it('should initialize isProcessing flag to false', () => {
      expect(manager.isProcessing).toBe(false);
    });
  });

  describe('handleTranslate()', () => {
    it('should prevent duplicate processing with race condition guard', async () => {
      manager.isProcessing = true;

      await manager.handleTranslate();

      expect(mockApiClient.translateText).not.toHaveBeenCalled();
      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'Processing already in progress. Please wait.'
      );
    });

    it('should validate input - require transcript', async () => {
      const editor = document.getElementById('transcript-editor');
      editor.value = '';
      mockState.transcription = '';

      await manager.handleTranslate();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'No text to translate. Please enter or upload audio first.'
      );
      expect(mockApiClient.translateText).not.toHaveBeenCalled();
    });

    it('should validate input - reject text over 50000 characters', async () => {
      const longText = 'a'.repeat(50001);
      const editor = document.getElementById('transcript-editor');
      editor.value = longText;

      await manager.handleTranslate();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'Text is too long. Maximum length is 50,000 characters.'
      );
      expect(mockApiClient.translateText).not.toHaveBeenCalled();
    });

    it('should call lockUI with correct operation name', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(uiLock.lockUI).toHaveBeenCalledWith('translating and generating audio');
    });

    it('should start ParticleSystem during processing', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(mockParticleSystem.start).toHaveBeenCalled();
    });

    it('should call API client translateText with correct parameters', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(mockApiClient.translateText).toHaveBeenCalledWith(
        'Test transcript',
        'Hebrew', // Capitalized
        'English' // Capitalized
      );
    });

    it('should call API client generateTTS with correct parameters', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(mockApiClient.generateTTS).toHaveBeenCalledWith(
        'Translated text',
        'alloy',
        'tts-1'
      );
    });

    it('should update state with translation and audio', async () => {
      const mockBlob = new Blob(['audio']);
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(mockBlob);

      await manager.handleTranslate();

      expect(mockState.translation).toBe('Translated text');
      expect(mockState.generatedAudioBlob).toBe(mockBlob);
      expect(mockState.generatedAudioUrl).toBe('blob:mock-url');
    });

    it('should save translation to session manager', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(mockSessionManager.saveState).toHaveBeenCalledWith('translation', 'Translated text');
    });

    it('should call UIStateManager.showResults on success', async () => {
      const mockAudioReactiveUI = { mock: 'audioReactiveUI' };
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate(mockAudioReactiveUI);

      expect(mockUIStateManager.showResults).toHaveBeenCalledWith(mockAudioReactiveUI);
    });

    it('should show loading messages for each step', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(mockUIFeedbackManager.showLoading).toHaveBeenCalledWith('Translating text...');
      expect(mockUIFeedbackManager.showLoading).toHaveBeenCalledWith('Generating speech...');
    });

    it('should stop ParticleSystem on completion', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(mockParticleSystem.stop).toHaveBeenCalled();
    });

    it('should hide loading overlay on completion', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(mockUIFeedbackManager.hideLoading).toHaveBeenCalled();
    });

    it('should call unlockUI on completion', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should reset isProcessing flag after completion', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      expect(manager.isProcessing).toBe(false);
      await manager.handleTranslate();
      expect(manager.isProcessing).toBe(false);
    });

    it('should handle translation API errors gracefully', async () => {
      const errorMessage = 'Translation service unavailable';
      mockApiClient.translateText.mockRejectedValue(new Error(errorMessage));

      await manager.handleTranslate();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        `Processing failed: ${errorMessage}`
      );
      expect(mockApiClient.generateTTS).not.toHaveBeenCalled();
    });

    it('should handle TTS API errors gracefully', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated text'
      });
      const errorMessage = 'TTS service unavailable';
      mockApiClient.generateTTS.mockRejectedValue(new Error(errorMessage));

      await manager.handleTranslate();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        `Processing failed: ${errorMessage}`
      );
    });

    it('should stop ParticleSystem on error', async () => {
      mockApiClient.translateText.mockRejectedValue(new Error('Test error'));

      await manager.handleTranslate();

      expect(mockParticleSystem.stop).toHaveBeenCalled();
    });

    it('should unlock UI on error (finally block)', async () => {
      mockApiClient.translateText.mockRejectedValue(new Error('Test error'));

      await manager.handleTranslate();

      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should reset isProcessing flag on error', async () => {
      mockApiClient.translateText.mockRejectedValue(new Error('Test error'));

      await manager.handleTranslate();

      expect(manager.isProcessing).toBe(false);
    });

    it('should read text from editor if available', async () => {
      const editor = document.getElementById('transcript-editor');
      editor.value = 'Editor text';
      mockState.transcription = 'State text';

      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await manager.handleTranslate();

      expect(mockApiClient.translateText).toHaveBeenCalledWith(
        'Editor text', // Should use editor value
        'Hebrew',
        'English'
      );
    });

    it('should work without ParticleSystem (optional dependency)', async () => {
      const managerWithoutParticles = new AudioProcessingManager(
        mockApiClient,
        mockUIStateManager,
        mockUIFeedbackManager,
        mockState,
        null, // No particle system
        mockSessionManager
      );

      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'Translated'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await managerWithoutParticles.handleTranslate();

      expect(mockState.translation).toBe('Translated');
    });
  });

  describe('handleDownload()', () => {
    beforeEach(() => {
      // Mock DOM methods
      document.body.appendChild = vi.fn();
      document.body.removeChild = vi.fn();
      document.createElement = vi.fn(() => {
        const element = {
          href: '',
          download: '',
          click: vi.fn()
        };
        return element;
      });
    });

    it('should download audio file when blob exists', () => {
      mockState.generatedAudioBlob = new Blob(['audio']);
      mockState.generatedAudioUrl = 'blob:mock-url';
      mockState.targetLanguage = 'english';

      manager.handleDownload();

      const createElement = document.createElement;
      expect(createElement).toHaveBeenCalledWith('a');
    });

    it('should show error when no audio to download', () => {
      mockState.generatedAudioBlob = null;

      manager.handleDownload();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith('No audio to download');
    });

    it('should create download link with correct filename format', () => {
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      };
      document.createElement = vi.fn(() => mockLink);

      mockState.generatedAudioBlob = new Blob(['audio']);
      mockState.generatedAudioUrl = 'blob:test-url';
      mockState.targetLanguage = 'english';

      // Mock Date.now()
      const mockTimestamp = 1234567890;
      vi.spyOn(Date, 'now').mockReturnValue(mockTimestamp);

      manager.handleDownload();

      expect(mockLink.href).toBe('blob:test-url');
      expect(mockLink.download).toBe(`dubbed_audio_english_${mockTimestamp}.mp3`);
    });
  });

  describe('reset()', () => {
    it('should reset isProcessing flag', () => {
      manager.isProcessing = true;
      manager.reset();
      expect(manager.isProcessing).toBe(false);
    });
  });

  describe('capitalize()', () => {
    it('should capitalize first letter of string', () => {
      expect(manager.capitalize('hello')).toBe('Hello');
      expect(manager.capitalize('world')).toBe('World');
    });

    it('should handle empty string', () => {
      expect(manager.capitalize('')).toBe('');
    });

    it('should handle null/undefined', () => {
      expect(manager.capitalize(null)).toBe('');
      expect(manager.capitalize(undefined)).toBe('');
    });

    it('should handle already capitalized strings', () => {
      expect(manager.capitalize('Hello')).toBe('Hello');
    });

    it('should only capitalize first character', () => {
      expect(manager.capitalize('hELLO')).toBe('HELLO');
    });
  });
});
