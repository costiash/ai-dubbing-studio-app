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

    // Set up DOM
    document.body.innerHTML = `
      <div id="waveform-container" style="display: none;"></div>
    `;

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

    it('should initialize isUploading flag to false', () => {
      expect(manager.isUploading).toBe(false);
    });
  });

  describe('handleFileUpload()', () => {
    it('should prevent duplicate uploads with race condition guard', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });

      // Set flag manually to simulate ongoing upload
      manager.isUploading = true;

      await manager.handleFileUpload(mockFile);

      // Should not proceed with upload
      expect(mockApiClient.transcribeAudio).not.toHaveBeenCalled();
      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        'Upload already in progress. Please wait.'
      );
    });

    it('should upload file successfully and update state', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Hello world',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(mockState.transcription).toBe('Hello world');
      expect(mockState.sourceLanguage).toBe('en');
      expect(mockState.originalFile).toBe(mockFile);
      expect(mockState.originalAudioUrl).toMatch(/^blob:/);
    });

    it('should call lockUI with correct operation name', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test transcription',
        language: 'he'
      });

      await manager.handleFileUpload(mockFile);

      expect(uiLock.lockUI).toHaveBeenCalledWith('uploading and transcribing');
    });

    it('should start WaveformVisualizer during upload', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(mockWaveformVisualizer.start).toHaveBeenCalled();
      const container = document.getElementById('waveform-container');
      expect(container.style.display).toBe('none'); // Hidden after completion
    });

    it('should call API client transcribeAudio with correct file', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(mockApiClient.transcribeAudio).toHaveBeenCalledWith(mockFile);
    });

    it('should show upload progress during transcription', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(mockUIFeedbackManager.showUploadProgress).toHaveBeenCalled();
    });

    it('should save state to session manager', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Hello world',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(mockSessionManager.saveState).toHaveBeenCalledWith('transcription', 'Hello world');
      expect(mockSessionManager.saveState).toHaveBeenCalledWith('sourceLanguage', 'en');
    });

    it('should call UIStateManager.showTranscriptionSection on success', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(mockUIStateManager.showTranscriptionSection).toHaveBeenCalled();
    });

    it('should stop WaveformVisualizer on completion', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(mockWaveformVisualizer.stop).toHaveBeenCalled();
    });

    it('should hide upload progress after completion', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(mockUIFeedbackManager.hideUploadProgress).toHaveBeenCalled();
    });

    it('should call unlockUI on completion', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      await manager.handleFileUpload(mockFile);

      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should reset isUploading flag after completion', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Test',
        language: 'en'
      });

      expect(manager.isUploading).toBe(false);
      await manager.handleFileUpload(mockFile);
      expect(manager.isUploading).toBe(false);
    });

    it('should handle API errors gracefully', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      const errorMessage = 'Network error';
      mockApiClient.transcribeAudio.mockRejectedValue(new Error(errorMessage));

      await manager.handleFileUpload(mockFile);

      expect(mockUIFeedbackManager.showError).toHaveBeenCalledWith(
        `Transcription failed: ${errorMessage}`
      );
    });

    it('should stop WaveformVisualizer on error', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockRejectedValue(new Error('Test error'));

      await manager.handleFileUpload(mockFile);

      expect(mockWaveformVisualizer.stop).toHaveBeenCalled();
    });

    it('should unlock UI on error (finally block)', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockRejectedValue(new Error('Test error'));

      await manager.handleFileUpload(mockFile);

      expect(uiLock.unlockUI).toHaveBeenCalled();
    });

    it('should reset isUploading flag on error', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockRejectedValue(new Error('Test error'));

      await manager.handleFileUpload(mockFile);

      expect(manager.isUploading).toBe(false);
    });

    it('should handle missing language in API response', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
      mockApiClient.transcribeAudio.mockResolvedValue({
        text: 'Hello world'
        // language is missing
      });

      await manager.handleFileUpload(mockFile);

      expect(mockState.sourceLanguage).toBe('hebrew'); // Default fallback
    });

    it('should work without WaveformVisualizer (optional dependency)', async () => {
      const mockFile = new File(['audio'], 'test.mp3', { type: 'audio/mp3' });
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

      await managerWithoutWaveform.handleFileUpload(mockFile);

      expect(mockState.transcription).toBe('Test');
    });
  });

  describe('reset()', () => {
    it('should reset isUploading flag', () => {
      manager.isUploading = true;
      manager.reset();
      expect(manager.isUploading).toBe(false);
    });
  });
});
