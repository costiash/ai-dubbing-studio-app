import { describe, it, expect, beforeEach, vi } from 'vitest';
import { FileUploadManager } from '../../scripts/managers/FileUploadManager.js';
import { AudioProcessingManager } from '../../scripts/managers/AudioProcessingManager.js';
import { UIStateManager } from '../../scripts/managers/UIStateManager.js';
import { UIFeedbackManager } from '../../scripts/managers/UIFeedbackManager.js';
import * as uiLock from '../../scripts/utils/ui-lock.js';

// Mock lockUI/unlockUI
vi.mock('../../scripts/utils/ui-lock.js', () => ({
  lockUI: vi.fn(),
  unlockUI: vi.fn()
}));

describe('App Workflow Integration Tests', () => {
  let mockApiClient;
  let mockState;
  let fileUploadManager;
  let audioProcessingManager;
  let uiStateManager;
  let uiFeedbackManager;
  let mockWaveformVisualizer;
  let mockParticleSystem;
  let mockSessionManager;
  let mockAudioPlayerLoader;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();

    // Set up complete DOM
    document.body.innerHTML = `
      <!-- Upload Section -->
      <section id="upload-section"></section>

      <!-- File Preview -->
      <div id="file-preview" class="hidden">
        <span id="file-preview-name"></span>
      </div>
      <button id="transcribe-btn" class="hidden"></button>
      <select id="audio-language">
        <option value="">Auto-detect</option>
        <option value="en">English</option>
        <option value="he">Hebrew</option>
      </select>

      <!-- Transcribe Section -->
      <section id="transcribe-section" class="hidden">
        <textarea id="transcript-editor"></textarea>
        <span id="char-count">0 / 50,000</span>
        <select id="source-language">
          <option value="hebrew">Hebrew</option>
          <option value="english">English</option>
        </select>
        <select id="target-language">
          <option value="english">English</option>
          <option value="hebrew">Hebrew</option>
        </select>
        <button id="translate-btn">Translate</button>
      </section>

      <!-- Results Section -->
      <section id="results-section" class="hidden">
        <div id="original-audio-player"></div>
        <div id="original-player-result"></div>
        <div id="generated-player"></div>
        <h3 id="original-title">Original Audio</h3>
        <h3 id="generated-title">Generated Audio</h3>
        <p id="original-transcript"></p>
        <p id="translated-transcript"></p>
        <button id="download-btn">Download</button>
        <button id="start-new-btn">Start New</button>
      </section>

      <!-- UI Feedback Elements -->
      <div id="loading-overlay" class="hidden"></div>
      <div id="loading-message"></div>
      <div id="upload-progress" class="hidden"></div>
      <div id="error-toast" class="hidden">
        <span id="error-message"></span>
      </div>
      <div id="waveform-container" style="display: none;"></div>
    `;

    // Mock URL APIs
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();

    // Create shared state
    mockState = {
      currentStep: 'upload',
      transcription: null,
      translation: null,
      sourceLanguage: null,
      targetLanguage: null,
      voice: 'alloy',
      model: 'tts-1',
      instructions: '',
      originalFile: null,
      originalAudioUrl: null,
      generatedAudioBlob: null,
      generatedAudioUrl: null,
      originalPlayer: null,
      originalPlayerResult: null,
      generatedPlayer: null
    };

    // Create mock API client
    mockApiClient = {
      transcribeAudio: vi.fn(),
      translateText: vi.fn(),
      generateTTS: vi.fn()
    };

    // Create mock visual effects
    mockWaveformVisualizer = {
      start: vi.fn(),
      stop: vi.fn()
    };

    mockParticleSystem = {
      start: vi.fn(),
      stop: vi.fn()
    };

    // Create mock session manager
    mockSessionManager = {
      saveState: vi.fn(),
      loadState: vi.fn(),
      clearState: vi.fn()
    };

    // Create mock audio player loader
    mockAudioPlayerLoader = vi.fn((id, url) => ({
      id,
      url,
      audio: {
        addEventListener: vi.fn()
      }
    }));

    // Create UI managers
    uiFeedbackManager = new UIFeedbackManager();
    uiStateManager = new UIStateManager(mockState, mockAudioPlayerLoader);

    // Create workflow managers
    fileUploadManager = new FileUploadManager(
      mockApiClient,
      uiStateManager,
      uiFeedbackManager,
      mockState,
      mockWaveformVisualizer,
      mockSessionManager
    );

    audioProcessingManager = new AudioProcessingManager(
      mockApiClient,
      uiStateManager,
      uiFeedbackManager,
      mockState,
      mockParticleSystem,
      mockSessionManager
    );
  });

  describe('Upload → Transcribe Flow (Two-Step)', () => {
    it('should store file on handleFileUpload (step 1)', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });

      await fileUploadManager.handleFileUpload(mockFile);

      // File should be stored but NOT transcribed yet
      expect(mockState.originalFile).toBe(mockFile);
      expect(mockState.originalAudioUrl).toBe('blob:mock-url');
      expect(mockApiClient.transcribeAudio).not.toHaveBeenCalled();

      // File preview should be visible
      expect(document.getElementById('file-preview').classList.contains('hidden')).toBe(false);
      expect(document.getElementById('transcribe-btn').classList.contains('hidden')).toBe(false);
    });

    it('should complete transcription on startTranscription (step 2)', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'שלום עולם',
        language: 'Hebrew'
      });

      // Step 1: Upload file
      await fileUploadManager.handleFileUpload(mockFile);

      // Step 2: Start transcription
      await fileUploadManager.startTranscription();

      // Verify state
      expect(mockState.transcription).toBe('שלום עולם');
      expect(mockState.sourceLanguage).toBe('hebrew');

      // Verify UI state
      expect(mockState.currentStep).toBe('transcribe');
      expect(document.getElementById('upload-section').classList.contains('hidden')).toBe(true);
      expect(document.getElementById('transcribe-section').classList.contains('hidden')).toBe(false);

      // Verify transcript editor populated
      const editor = document.getElementById('transcript-editor');
      expect(editor.value).toBe('שלום עולם');

      // Verify UI locking
      expect(uiLock.lockUI).toHaveBeenCalledWith('transcribing audio');
      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should handle transcription errors gracefully', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockRejectedValue(new Error('API Error'));

      const showErrorSpy = vi.spyOn(uiFeedbackManager, 'showError');

      // Step 1: Upload file
      await fileUploadManager.handleFileUpload(mockFile);

      // Step 2: Start transcription (fails)
      await fileUploadManager.startTranscription();

      // Should show error
      expect(showErrorSpy).toHaveBeenCalledWith('Transcription failed: API Error');

      // Should unlock UI
      expect(uiLock.unlockUI).toHaveBeenCalled();

      // Should not change step
      expect(mockState.currentStep).toBe('upload');
    });

    it('should prevent duplicate transcriptions', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockImplementation(() =>
        new Promise(resolve => setTimeout(() => resolve({ text: 'test', language: 'en' }), 100))
      );

      // Step 1: Upload file
      await fileUploadManager.handleFileUpload(mockFile);

      // Start first transcription (don't await)
      const firstTranscription = fileUploadManager.startTranscription();

      // Try second transcription immediately
      const secondTranscription = fileUploadManager.startTranscription();

      await Promise.all([firstTranscription, secondTranscription]);

      // API should only be called once
      expect(mockApiClient.transcribeAudio).toHaveBeenCalledTimes(1);
    });
  });

  describe('Translate → TTS Flow', () => {
    beforeEach(() => {
      // Set up state as if transcription is complete
      mockState.transcription = 'Hello world';
      mockState.sourceLanguage = 'hebrew';
      mockState.targetLanguage = 'english';
      mockState.currentStep = 'transcribe';

      const editor = document.getElementById('transcript-editor');
      editor.value = 'Hello world';

      // Set DOM select values to match state
      document.getElementById('source-language').value = 'hebrew';
      document.getElementById('target-language').value = 'english';
    });

    it('should complete translation and TTS generation', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'שלום עולם'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await audioProcessingManager.handleTranslate();

      // Verify translation
      expect(mockApiClient.translateText).toHaveBeenCalledWith(
        'Hello world',
        'Hebrew',
        'English'
      );
      expect(mockState.translation).toBe('שלום עולם');

      // Verify TTS
      expect(mockApiClient.generateTTS).toHaveBeenCalledWith(
        'שלום עולם',
        'alloy',
        'tts-1',
        null // instructions (empty string becomes null)
      );
      expect(mockState.generatedAudioBlob).toBeTruthy();
      expect(mockState.generatedAudioUrl).toMatch(/^blob:/);

      // Verify UI state
      expect(mockState.currentStep).toBe('results');
      expect(document.getElementById('results-section').classList.contains('hidden')).toBe(false);

      // Verify UI locking
      expect(uiLock.lockUI).toHaveBeenCalledWith('translating and generating audio');
      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should handle translation errors', async () => {
      mockApiClient.translateText.mockRejectedValue(new Error('Translation service down'));

      const showErrorSpy = vi.spyOn(uiFeedbackManager, 'showError');

      await audioProcessingManager.handleTranslate();

      expect(showErrorSpy).toHaveBeenCalledWith('Processing failed: Translation service down');
      expect(mockApiClient.generateTTS).not.toHaveBeenCalled();
      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should handle TTS errors', async () => {
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'שלום עולם'
      });
      mockApiClient.generateTTS.mockRejectedValue(new Error('TTS service down'));

      const showErrorSpy = vi.spyOn(uiFeedbackManager, 'showError');

      await audioProcessingManager.handleTranslate();

      expect(showErrorSpy).toHaveBeenCalledWith('Processing failed: TTS service down');
      expect(mockState.translation).toBe('שלום עולם'); // Translation should still be saved
      expect(mockState.generatedAudioBlob).toBeNull();
      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should prevent duplicate processing', async () => {
      mockApiClient.translateText.mockImplementation(() =>
        new Promise(resolve => setTimeout(() => resolve({ translated_text: 'test' }), 100))
      );
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      // Start first processing (don't await)
      const firstProcess = audioProcessingManager.handleTranslate();

      // Try second processing immediately
      const secondProcess = audioProcessingManager.handleTranslate();

      await Promise.all([firstProcess, secondProcess]);

      // API should only be called once
      expect(mockApiClient.translateText).toHaveBeenCalledTimes(1);
    });
  });

  describe('Full End-to-End Flow', () => {
    it('should complete entire workflow: Upload → Transcribe → Translate → TTS', async () => {
      // Step 1: Upload file
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });

      await fileUploadManager.handleFileUpload(mockFile);
      expect(mockState.originalFile).toBe(mockFile);

      // Step 2: Transcribe
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Hello world',
        language: 'English'
      });

      await fileUploadManager.startTranscription();

      expect(mockState.currentStep).toBe('transcribe');
      expect(mockState.transcription).toBe('Hello world');

      // Step 3: Translate and generate TTS
      mockState.targetLanguage = 'hebrew';
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'שלום עולם'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await audioProcessingManager.handleTranslate();

      expect(mockState.currentStep).toBe('results');
      expect(mockState.translation).toBe('שלום עולם');
      expect(mockState.generatedAudioBlob).toBeTruthy();

      // Verify all API calls
      expect(mockApiClient.transcribeAudio).toHaveBeenCalledTimes(1);
      expect(mockApiClient.translateText).toHaveBeenCalledTimes(1);
      expect(mockApiClient.generateTTS).toHaveBeenCalledTimes(1);

      // Verify session persistence
      expect(mockSessionManager.saveState).toHaveBeenCalledWith('transcription', 'Hello world');
      expect(mockSessionManager.saveState).toHaveBeenCalledWith('translation', 'שלום עולם');

      // Verify results section is visible
      expect(document.getElementById('results-section').classList.contains('hidden')).toBe(false);
      expect(document.getElementById('original-transcript').textContent).toBe('Hello world');
      expect(document.getElementById('translated-transcript').textContent).toBe('שלום עולם');
    });
  });

  describe('Download Workflow', () => {
    beforeEach(() => {
      // Set up state as if processing is complete
      mockState.generatedAudioBlob = new Blob(['audio']);
      mockState.generatedAudioUrl = 'blob:test-url';
      mockState.targetLanguage = 'hebrew';

      // Mock DOM methods
      document.body.appendChild = vi.fn();
      document.body.removeChild = vi.fn();
      document.createElement = vi.fn(() => ({
        href: '',
        download: '',
        click: vi.fn()
      }));
    });

    it('should download generated audio file', () => {
      audioProcessingManager.handleDownload();

      expect(document.createElement).toHaveBeenCalledWith('a');
    });

    it('should show error when no audio to download', () => {
      mockState.generatedAudioBlob = null;

      const showErrorSpy = vi.spyOn(uiFeedbackManager, 'showError');

      audioProcessingManager.handleDownload();

      expect(showErrorSpy).toHaveBeenCalledWith('No audio to download');
    });
  });

  describe('Reset Workflow', () => {
    it('should reset UI to initial state', () => {
      // Set up state as if in results
      mockState.currentStep = 'results';
      document.getElementById('upload-section').classList.add('hidden');
      document.getElementById('results-section').classList.remove('hidden');

      const editor = document.getElementById('transcript-editor');
      editor.value = 'Some text';

      // Reset
      uiStateManager.reset();

      // Verify UI reset
      expect(document.getElementById('upload-section').classList.contains('hidden')).toBe(false);
      expect(document.getElementById('transcribe-section').classList.contains('hidden')).toBe(true);
      expect(document.getElementById('results-section').classList.contains('hidden')).toBe(true);

      // Verify editor cleared
      expect(editor.value).toBe('');
    });

    it('should reset manager flags', () => {
      fileUploadManager.isTranscribing = true;
      audioProcessingManager.isProcessing = true;

      fileUploadManager.reset();
      audioProcessingManager.reset();

      expect(fileUploadManager.isTranscribing).toBe(false);
      expect(audioProcessingManager.isProcessing).toBe(false);
    });
  });

  describe('Error Recovery', () => {
    it('should recover from transcription error and allow retry', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });

      // Upload file first
      await fileUploadManager.handleFileUpload(mockFile);

      // First transcription attempt fails
      mockApiClient.transcribeAudio.mockRejectedValueOnce(new Error('Network error'));

      await fileUploadManager.startTranscription();

      expect(fileUploadManager.isTranscribing).toBe(false);
      expect(uiLock.unlockUI).toHaveBeenCalled();

      // Clear mocks
      vi.clearAllMocks();

      // Second attempt succeeds
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Success',
        language: 'English'
      });

      await fileUploadManager.startTranscription();

      expect(mockState.transcription).toBe('Success');
      expect(mockState.currentStep).toBe('transcribe');
    });

    it('should recover from processing error and allow retry', async () => {
      mockState.transcription = 'Hello';
      mockState.targetLanguage = 'hebrew';

      const editor = document.getElementById('transcript-editor');
      editor.value = 'Hello';

      // First attempt fails
      mockApiClient.translateText.mockRejectedValueOnce(new Error('API error'));

      await audioProcessingManager.handleTranslate();

      expect(audioProcessingManager.isProcessing).toBe(false);
      expect(uiLock.unlockUI).toHaveBeenCalled();

      // Clear mocks
      vi.clearAllMocks();

      // Second attempt succeeds
      mockApiClient.translateText.mockResolvedValue({
        translated_text: 'שלום'
      });
      mockApiClient.generateTTS.mockResolvedValue(new Blob(['audio']));

      await audioProcessingManager.handleTranslate();

      expect(mockState.translation).toBe('שלום');
      expect(mockState.currentStep).toBe('results');
    });
  });
});
