import { describe, it, expect, beforeEach, vi } from 'vitest';
import { UIStateManager } from '../../scripts/managers/UIStateManager.js';

describe('UIStateManager', () => {
  let manager;
  let mockState;
  let mockAudioPlayerLoader;

  beforeEach(() => {
    // Set up DOM
    document.body.innerHTML = `
      <section id="upload-section" class="hidden"></section>
      <section id="transcribe-section" class="hidden"></section>
      <section id="results-section" class="hidden"></section>
      <textarea id="transcript-editor"></textarea>
      <span id="char-count">0 / 50,000</span>
      <select id="source-language">
        <option value="hebrew">Hebrew</option>
        <option value="english">English</option>
      </select>
      <div id="original-audio-player"></div>
      <div id="original-player-result"></div>
      <div id="generated-player"></div>
      <h3 id="original-title">Original Audio</h3>
      <h3 id="generated-title">Generated Audio</h3>
      <p id="original-transcript"></p>
      <p id="translated-transcript"></p>
    `;

    // Create mocks
    mockState = {
      currentStep: 'upload',
      transcription: 'Test transcription',
      translation: 'Test translation',
      sourceLanguage: 'hebrew',
      targetLanguage: 'english',
      originalAudioUrl: 'blob:original-url',
      generatedAudioUrl: 'blob:generated-url',
      originalPlayer: null,
      originalPlayerResult: null,
      generatedPlayer: null
    };

    mockAudioPlayerLoader = vi.fn((id, url) => ({
      id,
      url,
      audio: {
        addEventListener: vi.fn()
      }
    }));

    // Create manager instance
    manager = new UIStateManager(mockState, mockAudioPlayerLoader);
  });

  describe('Constructor', () => {
    it('should initialize with state and audio player loader', () => {
      expect(manager.state).toBe(mockState);
      expect(manager.loadAudioPlayer).toBe(mockAudioPlayerLoader);
    });
  });

  describe('showTranscriptionSection()', () => {
    it('should update currentStep to transcribe', () => {
      manager.showTranscriptionSection();
      expect(mockState.currentStep).toBe('transcribe');
    });

    it('should hide upload section and show transcribe section', () => {
      manager.showTranscriptionSection();

      const uploadSection = document.getElementById('upload-section');
      const transcribeSection = document.getElementById('transcribe-section');

      expect(uploadSection.classList.contains('hidden')).toBe(true);
      expect(transcribeSection.classList.contains('hidden')).toBe(false);
    });

    it('should populate transcript editor with transcription', () => {
      manager.showTranscriptionSection();

      const editor = document.getElementById('transcript-editor');
      expect(editor.value).toBe('Test transcription');
    });

    it('should update character count', () => {
      manager.showTranscriptionSection();

      const charCount = document.getElementById('char-count');
      expect(charCount.textContent).toBe('18 / 50,000');
    });

    it('should set source language in select', () => {
      manager.showTranscriptionSection();

      const sourceLangSelect = document.getElementById('source-language');
      expect(sourceLangSelect.value).toBe('hebrew');
    });

    it('should load audio player for original audio', () => {
      manager.showTranscriptionSection();

      expect(mockAudioPlayerLoader).toHaveBeenCalledWith(
        'original-audio-player',
        'blob:original-url'
      );
      expect(mockState.originalPlayer).toBeTruthy();
    });

    it('should handle missing audio URL gracefully', () => {
      mockState.originalAudioUrl = null;

      expect(() => manager.showTranscriptionSection()).not.toThrow();
      expect(mockAudioPlayerLoader).not.toHaveBeenCalled();
    });
  });

  describe('updateCharCount()', () => {
    it('should update character count display', () => {
      const editor = document.getElementById('transcript-editor');
      editor.value = 'Hello world';

      manager.updateCharCount();

      const charCount = document.getElementById('char-count');
      expect(charCount.textContent).toBe('11 / 50,000');
    });

    it('should add error class when over limit', () => {
      const editor = document.getElementById('transcript-editor');
      editor.value = 'a'.repeat(50001);

      manager.updateCharCount();

      const charCount = document.getElementById('char-count');
      expect(charCount.classList.contains('transcript-box__char-count--error')).toBe(true);
    });

    it('should add warning class when over 90% of limit', () => {
      const editor = document.getElementById('transcript-editor');
      editor.value = 'a'.repeat(45001); // Over 90% of 50000

      manager.updateCharCount();

      const charCount = document.getElementById('char-count');
      expect(charCount.classList.contains('transcript-box__char-count--warning')).toBe(true);
    });

    it('should remove warning/error classes when below thresholds', () => {
      const editor = document.getElementById('transcript-editor');
      const charCount = document.getElementById('char-count');

      // Set error class
      editor.value = 'a'.repeat(50001);
      manager.updateCharCount();
      expect(charCount.classList.contains('transcript-box__char-count--error')).toBe(true);

      // Update to valid count
      editor.value = 'Hello';
      manager.updateCharCount();
      expect(charCount.classList.contains('transcript-box__char-count--error')).toBe(false);
    });

    it('should handle missing elements gracefully', () => {
      document.body.innerHTML = '';
      expect(() => manager.updateCharCount()).not.toThrow();
    });

    it('should use locale formatting for numbers', () => {
      const editor = document.getElementById('transcript-editor');
      editor.value = 'a'.repeat(1000);

      manager.updateCharCount();

      const charCount = document.getElementById('char-count');
      expect(charCount.textContent).toBe('1,000 / 50,000');
    });
  });

  describe('showResults()', () => {
    let mockAudioReactiveUI;

    beforeEach(() => {
      mockAudioReactiveUI = {
        start: vi.fn(),
        stop: vi.fn()
      };
    });

    it('should update currentStep to results', () => {
      manager.showResults(mockAudioReactiveUI);
      expect(mockState.currentStep).toBe('results');
    });

    it('should hide transcribe section and show results section', () => {
      manager.showResults(mockAudioReactiveUI);

      const transcribeSection = document.getElementById('transcribe-section');
      const resultsSection = document.getElementById('results-section');

      expect(transcribeSection.classList.contains('hidden')).toBe(true);
      expect(resultsSection.classList.contains('hidden')).toBe(false);
    });

    it('should update original audio title with source language', () => {
      manager.showResults(mockAudioReactiveUI);

      const originalTitle = document.getElementById('original-title');
      expect(originalTitle.textContent).toBe('Original Audio (Hebrew)');
    });

    it('should update generated audio title with target language', () => {
      manager.showResults(mockAudioReactiveUI);

      const generatedTitle = document.getElementById('generated-title');
      expect(generatedTitle.textContent).toBe('Generated Audio (English)');
    });

    it('should display transcription text', () => {
      manager.showResults(mockAudioReactiveUI);

      const originalTranscript = document.getElementById('original-transcript');
      expect(originalTranscript.textContent).toBe('Test transcription');
    });

    it('should display translation text', () => {
      manager.showResults(mockAudioReactiveUI);

      const translatedTranscript = document.getElementById('translated-transcript');
      expect(translatedTranscript.textContent).toBe('Test translation');
    });

    it('should load audio player for original audio', () => {
      manager.showResults(mockAudioReactiveUI);

      expect(mockAudioPlayerLoader).toHaveBeenCalledWith(
        'original-player-result',
        'blob:original-url'
      );
      expect(mockState.originalPlayerResult).toBeTruthy();
    });

    it('should load audio player for generated audio', () => {
      manager.showResults(mockAudioReactiveUI);

      expect(mockAudioPlayerLoader).toHaveBeenCalledWith(
        'generated-player',
        'blob:generated-url'
      );
      expect(mockState.generatedPlayer).toBeTruthy();
    });

    it('should wire up AudioReactiveUI to audio events', () => {
      manager.showResults(mockAudioReactiveUI);

      const originalPlayer = mockState.originalPlayerResult;
      const generatedPlayer = mockState.generatedPlayer;

      // Check that event listeners were added
      expect(originalPlayer.audio.addEventListener).toHaveBeenCalledWith('play', expect.any(Function));
      expect(originalPlayer.audio.addEventListener).toHaveBeenCalledWith('pause', expect.any(Function));
      expect(originalPlayer.audio.addEventListener).toHaveBeenCalledWith('ended', expect.any(Function));

      expect(generatedPlayer.audio.addEventListener).toHaveBeenCalledWith('play', expect.any(Function));
      expect(generatedPlayer.audio.addEventListener).toHaveBeenCalledWith('pause', expect.any(Function));
      expect(generatedPlayer.audio.addEventListener).toHaveBeenCalledWith('ended', expect.any(Function));
    });

    it('should start AudioReactiveUI on play event', () => {
      manager.showResults(mockAudioReactiveUI);

      const originalPlayer = mockState.originalPlayerResult;
      const playHandler = originalPlayer.audio.addEventListener.mock.calls.find(
        call => call[0] === 'play'
      )[1];

      playHandler();
      expect(mockAudioReactiveUI.start).toHaveBeenCalledWith(originalPlayer.audio);
    });

    it('should stop AudioReactiveUI on pause event', () => {
      manager.showResults(mockAudioReactiveUI);

      const originalPlayer = mockState.originalPlayerResult;
      const pauseHandler = originalPlayer.audio.addEventListener.mock.calls.find(
        call => call[0] === 'pause'
      )[1];

      pauseHandler();
      expect(mockAudioReactiveUI.stop).toHaveBeenCalled();
    });

    it('should stop AudioReactiveUI on ended event', () => {
      manager.showResults(mockAudioReactiveUI);

      const originalPlayer = mockState.originalPlayerResult;
      const endedHandler = originalPlayer.audio.addEventListener.mock.calls.find(
        call => call[0] === 'ended'
      )[1];

      endedHandler();
      expect(mockAudioReactiveUI.stop).toHaveBeenCalled();
    });

    it('should work without AudioReactiveUI', () => {
      expect(() => manager.showResults(null)).not.toThrow();
    });

    it('should handle missing audio URLs gracefully', () => {
      mockState.originalAudioUrl = null;
      mockState.generatedAudioUrl = null;

      expect(() => manager.showResults(mockAudioReactiveUI)).not.toThrow();
    });
  });

  describe('reset()', () => {
    it('should show upload section and hide others', () => {
      manager.reset();

      const uploadSection = document.getElementById('upload-section');
      const transcribeSection = document.getElementById('transcribe-section');
      const resultsSection = document.getElementById('results-section');

      expect(uploadSection.classList.contains('hidden')).toBe(false);
      expect(transcribeSection.classList.contains('hidden')).toBe(true);
      expect(resultsSection.classList.contains('hidden')).toBe(true);
    });

    it('should clear transcript editor', () => {
      const editor = document.getElementById('transcript-editor');
      editor.value = 'Some text';

      manager.reset();

      expect(editor.value).toBe('');
    });

    it('should update character count after clearing', () => {
      const editor = document.getElementById('transcript-editor');
      editor.value = 'Some text';

      manager.reset();

      const charCount = document.getElementById('char-count');
      expect(charCount.textContent).toBe('0 / 50,000');
    });

    it('should handle missing editor gracefully', () => {
      document.getElementById('transcript-editor').remove();
      expect(() => manager.reset()).not.toThrow();
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
