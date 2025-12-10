import { describe, it, expect, beforeEach, vi } from 'vitest';
import { FileUploadManager } from '../../scripts/managers/FileUploadManager.js';
import * as uiLock from '../../scripts/utils/ui-lock.js';

// Mock lockUI/unlockUI
vi.mock('../../scripts/utils/ui-lock.js', () => ({
  lockUI: vi.fn(),
  unlockUI: vi.fn()
}));

describe('FileUploadManager', () => {
  let manager;
  let mockApiClient;
  let mockUIStateManager;
  let mockUIFeedbackManager;
  let mockState;
  let mockWaveformVisualizer;
  let mockSessionManager;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();

    // Set up DOM with all required elements
    document.body.innerHTML = `
      <div id="waveform-container" style="display: none;"></div>
      <div id="file-preview" class="hidden">
        <span id="file-preview-name"></span>
      </div>
      <button id="transcribe-btn" class="hidden"></button>
      <select id="audio-language">
        <option value="">Auto-detect</option>
        <option value="en">English</option>
        <option value="he">Hebrew</option>
      </select>
    `;

    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();

    // Create mocks
    mockApiClient = {
      transcribeAudio: vi.fn()
    };

    mockUIStateManager = {
      showTranscriptionSection: vi.fn()
    };

    mockUIFeedbackManager = {
      showUploadProgress: vi.fn(),
      hideUploadProgress: vi.fn(),
      showError: vi.fn()
    };

    mockState = {
      transcription: null,
      sourceLanguage: null,
      originalFile: null,
      originalAudioUrl: null
    };

    mockWaveformVisualizer = {
      start: vi.fn(),
      stop: vi.fn()
    };

    mockSessionManager = {
      saveState: vi.fn()
    };

    // Create manager instance
    manager = new FileUploadManager(
      mockApiClient,
      mockUIStateManager,
      mockUIFeedbackManager,
      mockState,
      mockWaveformVisualizer,
      mockSessionManager
    );
  });

  describe('Constructor', () => {
    it('should initialize with all dependencies', () => {
      expect(manager.apiClient).toBe(mockApiClient);
      expect(manager.uiStateManager).toBe(mockUIStateManager);
      expect(manager.uiFeedbackManager).toBe(mockUIFeedbackManager);
      expect(manager.state).toBe(mockState);
      expect(manager.waveformVisualizer).toBe(mockWaveformVisualizer);
      expect(manager.sessionManager).toBe(mockSessionManager);
    });

    it('should initialize isTranscribing flag to false', () => {
      expect(manager.isTranscribing).toBe(false);
    });
  });

  describe('handleFileUpload()', () => {
    it('should store file in state', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });

      await manager.handleFileUpload(mockFile);

      expect(mockState.originalFile).toBe(mockFile);
      expect(mockState.originalAudioUrl).toBe('blob:mock-url');
    });

    it('should show file preview with filename', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });

      await manager.handleFileUpload(mockFile);

      const filePreview = document.getElementById('file-preview');
      const fileName = document.getElementById('file-preview-name');
      expect(filePreview.classList.contains('hidden')).toBe(false);
      expect(fileName.textContent).toBe('test.mp3');
    });

    it('should show transcribe button', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });

      await manager.handleFileUpload(mockFile);

      const transcribeBtn = document.getElementById('transcribe-btn');
      expect(transcribeBtn.classList.contains('hidden')).toBe(false);
    });

    it('should NOT call transcribeAudio API (two-step workflow)', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });

      await manager.handleFileUpload(mockFile);

      // handleFileUpload should NOT call the API - that's startTranscription's job
      expect(mockApiClient.transcribeAudio).not.toHaveBeenCalled();
    });
  });

  describe('startTranscription()', () => {
    beforeEach(() => {
      // Set up file in state (simulating handleFileUpload was called)
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockState.originalFile = mockFile;
      mockState.originalAudioUrl = 'blob:mock-url';
    });

    it('should prevent duplicate transcriptions with race condition guard', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      // Set flag manually to simulate ongoing transcription
      manager.isTranscribing = true;

      await manager.startTranscription();

      // Should not proceed with transcription
      expect(mockApiClient.transcribeAudio).not.toHaveBeenCalled();
      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'Transcription already in progress. Please wait.'
      );
    });

    it('should show error if no file is selected', async () => {
      mockState.originalFile = null;

      await manager.startTranscription();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'No file selected. Please upload an audio file first.'
      );
      expect(mockApiClient.transcribeAudio).not.toHaveBeenCalled();
    });

    it('should transcribe file successfully and update state', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Hello world',
        language: 'English'
      });

      await manager.startTranscription();

      expect(mockState.transcription).toBe('Hello world');
      expect(mockState.sourceLanguage).toBe('english');
    });

    it('should call lockUI with correct operation name', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test transcription',
        language: 'he'
      });

      await manager.startTranscription();

      expect(uiLock.lockUI).toHaveBeenCalledWith('transcribing audio');
    });

    it('should start WaveformVisualizer during transcription', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.startTranscription();

      expect(mockWaveformVisualizer.start).toHaveBeenCalled();
    });

    it('should call API client transcribeAudio with correct file and language', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      // Set language dropdown to English
      document.getElementById('audio-language').value = 'en';

      await manager.startTranscription();

      expect(mockApiClient.transcribeAudio).toHaveBeenCalledWith(mockState.originalFile, 'en');
    });

    it('should call API with null language for auto-detect', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      // Set language dropdown to auto-detect (empty value)
      document.getElementById('audio-language').value = '';

      await manager.startTranscription();

      expect(mockApiClient.transcribeAudio).toHaveBeenCalledWith(mockState.originalFile, null);
    });

    it('should show upload progress during transcription', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.startTranscription();

      expect(mockUIFeedbackManager.showUploadProgress).toHaveBeenCalled();
    });

    it('should save state to session manager', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Hello world',
        language: 'English'
      });

      await manager.startTranscription();

      expect(mockSessionManager.saveState).toHaveBeenCalledWith('transcription', 'Hello world');
      expect(mockSessionManager.saveState).toHaveBeenCalledWith('sourceLanguage', 'english');
    });

    it('should call UIStateManager.showTranscriptionSection on success', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.startTranscription();

      expect(mockUIStateManager.showTranscriptionSection).toHaveBeenCalled();
    });

    it('should stop WaveformVisualizer on completion', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.startTranscription();

      expect(mockWaveformVisualizer.stop).toHaveBeenCalled();
    });

    it('should hide upload progress after completion', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.startTranscription();

      expect(mockUIFeedbackManager.hideUploadProgress).toHaveBeenCalled();
    });

    it('should call unlockUI on completion', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.startTranscription();

      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should reset isTranscribing flag after completion', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      expect(manager.isTranscribing).toBe(false);
      await manager.startTranscription();
      expect(manager.isTranscribing).toBe(false);
    });

    it('should handle API errors gracefully', async () => {
      const errorMessage = 'Network error';
      mockApiClient.transcribeAudio.mockRejectedValue(new Error(errorMessage));

      await manager.startTranscription();

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        `Transcription failed: ${errorMessage}`
      );
    });

    it('should stop WaveformVisualizer on error', async () => {
      mockApiClient.transcribeAudio.mockRejectedValue(new Error('Test error'));

      await manager.startTranscription();

      expect(mockWaveformVisualizer.stop).toHaveBeenCalled();
    });

    it('should unlock UI on error (finally block)', async () => {
      mockApiClient.transcribeAudio.mockRejectedValue(new Error('Test error'));

      await manager.startTranscription();

      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should reset isTranscribing flag on error', async () => {
      mockApiClient.transcribeAudio.mockRejectedValue(new Error('Test error'));

      await manager.startTranscription();

      expect(manager.isTranscribing).toBe(false);
    });

    it('should handle missing language in API response', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Hello world'
        // language is missing
      });

      await manager.startTranscription();

      expect(mockState.sourceLanguage).toBe('hebrew'); // Default fallback
    });

    it('should work without WaveformVisualizer (optional dependency)', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      // Create manager without WaveformVisualizer
      const managerWithoutWaveform = new FileUploadManager(
        mockApiClient,
        mockUIStateManager,
        mockUIFeedbackManager,
        mockState,
        null, // No waveform visualizer
        mockSessionManager
      );

      await managerWithoutWaveform.startTranscription();

      expect(mockState.transcription).toBe('Test');
    });

    it('should hide file preview after successful transcription', async () => {
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      // Show file preview first
      const filePreview = document.getElementById('file-preview');
      filePreview.classList.remove('hidden');

      await manager.startTranscription();

      expect(filePreview.classList.contains('hidden')).toBe(true);
    });

    it('should show transcribe button again on error for retry', async () => {
      mockApiClient.transcribeAudio.mockRejectedValue(new Error('Test error'));

      // Hide button first (simulating it was hidden when transcription started)
      const transcribeBtn = document.getElementById('transcribe-btn');
      transcribeBtn.classList.add('hidden');

      await manager.startTranscription();

      expect(transcribeBtn.classList.contains('hidden')).toBe(false);
    });
  });

  describe('removeFile()', () => {
    it('should clear file from state', () => {
      mockState.originalFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockState.originalAudioUrl = 'blob:mock-url';

      manager.removeFile();

      expect(mockState.originalFile).toBeNull();
      expect(mockState.originalAudioUrl).toBeNull();
    });

    it('should revoke object URL', () => {
      mockState.originalAudioUrl = 'blob:mock-url';

      manager.removeFile();

      expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:mock-url');
    });

    it('should hide file preview', () => {
      const filePreview = document.getElementById('file-preview');
      filePreview.classList.remove('hidden');

      manager.removeFile();

      expect(filePreview.classList.contains('hidden')).toBe(true);
    });

    it('should hide transcribe button', () => {
      const transcribeBtn = document.getElementById('transcribe-btn');
      transcribeBtn.classList.remove('hidden');

      manager.removeFile();

      expect(transcribeBtn.classList.contains('hidden')).toBe(true);
    });
  });

  describe('reset()', () => {
    it('should reset isTranscribing flag', () => {
      manager.isTranscribing = true;
      manager.reset();
      expect(manager.isTranscribing).toBe(false);
    });

    it('should call removeFile', () => {
      const removeFileSpy = vi.spyOn(manager, 'removeFile');
      manager.reset();
      expect(removeFileSpy).toHaveBeenCalled();
    });
  });
});
