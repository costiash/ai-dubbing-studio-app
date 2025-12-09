import { describe, it, expect, beforeEach } from 'vitest';
import { lockUI, unlockUI } from '../../scripts/utils/ui-lock.js';

describe('ui-lock.js', () => {
  beforeEach(() => {
    // Set up DOM with all required elements
    document.body.innerHTML = `
      <button id="translate-btn"></button>
      <button id="download-btn"></button>
      <button id="start-new-btn"></button>
      <div id="upload-zone" class="upload-zone" tabindex="0"></div>
      <input id="file-input" type="file" />
      <select id="source-language"></select>
      <select id="target-language"></select>
      <select id="voice-select"></select>
      <select id="model-select"></select>
      <textarea id="transcript-editor"></textarea>
    `;
  });

  describe('lockUI()', () => {
    it('should disable all buttons', () => {
      lockUI('testing');

      expect(document.getElementById('translate-btn').disabled).toBe(true);
      expect(document.getElementById('download-btn').disabled).toBe(true);
      expect(document.getElementById('start-new-btn').disabled).toBe(true);
    });

    it('should disable all form selectors', () => {
      lockUI('testing');

      expect(document.getElementById('source-language').disabled).toBe(true);
      expect(document.getElementById('target-language').disabled).toBe(true);
      expect(document.getElementById('voice-select').disabled).toBe(true);
      expect(document.getElementById('model-select').disabled).toBe(true);
    });

    it('should disable upload zone with correct class and attributes', () => {
      lockUI('testing');

      const dropZone = document.getElementById('upload-zone');
      expect(dropZone.classList.contains('upload-zone--disabled')).toBe(true);
      expect(dropZone.getAttribute('aria-disabled')).toBe('true');
      expect(dropZone.getAttribute('tabindex')).toBe('-1');
    });

    it('should disable file input', () => {
      lockUI('testing');

      expect(document.getElementById('file-input').disabled).toBe(true);
    });

    it('should disable transcript textarea', () => {
      lockUI('testing');

      expect(document.getElementById('transcript-editor').disabled).toBe(true);
    });

    it('should set ARIA attributes on translate button', () => {
      lockUI('uploading and transcribing');

      const btn = document.getElementById('translate-btn');
      expect(btn.getAttribute('aria-busy')).toBe('true');
      expect(btn.getAttribute('aria-label')).toBe('Currently uploading and transcribing...');
    });

    it('should use default operation name when not provided', () => {
      lockUI();

      const btn = document.getElementById('translate-btn');
      expect(btn.getAttribute('aria-label')).toBe('Currently processing...');
    });

    it('should handle missing elements gracefully', () => {
      document.body.innerHTML = ''; // Remove all elements

      // Should not throw errors
      expect(() => lockUI('testing')).not.toThrow();
    });

    it('should handle partially missing elements gracefully', () => {
      document.body.innerHTML = `
        <button id="translate-btn"></button>
      `;

      // Should not throw errors
      expect(() => lockUI('testing')).not.toThrow();
      expect(document.getElementById('translate-btn').disabled).toBe(true);
    });
  });

  describe('unlockUI()', () => {
    it('should re-enable all buttons after lockUI', () => {
      lockUI('testing');
      unlockUI();

      expect(document.getElementById('translate-btn').disabled).toBe(false);
      expect(document.getElementById('download-btn').disabled).toBe(false);
      expect(document.getElementById('start-new-btn').disabled).toBe(false);
    });

    it('should re-enable all form selectors', () => {
      lockUI('testing');
      unlockUI();

      expect(document.getElementById('source-language').disabled).toBe(false);
      expect(document.getElementById('target-language').disabled).toBe(false);
      expect(document.getElementById('voice-select').disabled).toBe(false);
      expect(document.getElementById('model-select').disabled).toBe(false);
    });

    it('should re-enable upload zone and restore tabindex', () => {
      lockUI('testing');
      unlockUI();

      const dropZone = document.getElementById('upload-zone');
      expect(dropZone.classList.contains('upload-zone--disabled')).toBe(false);
      expect(dropZone.getAttribute('aria-disabled')).toBeNull();
      expect(dropZone.getAttribute('tabindex')).toBe('0');
    });

    it('should re-enable file input', () => {
      lockUI('testing');
      unlockUI();

      expect(document.getElementById('file-input').disabled).toBe(false);
    });

    it('should re-enable transcript textarea', () => {
      lockUI('testing');
      unlockUI();

      expect(document.getElementById('transcript-editor').disabled).toBe(false);
    });

    it('should remove aria-busy from translate button', () => {
      lockUI('testing');
      unlockUI();

      const btn = document.getElementById('translate-btn');
      expect(btn.getAttribute('aria-busy')).toBeNull();
    });

    it('should restore correct aria-label on translate button', () => {
      lockUI('testing');
      unlockUI();

      const btn = document.getElementById('translate-btn');
      expect(btn.getAttribute('aria-label')).toBe('Translate and generate audio');
    });

    it('should handle missing elements gracefully', () => {
      lockUI('testing');
      document.body.innerHTML = ''; // Remove all elements

      // Should not throw errors
      expect(() => unlockUI()).not.toThrow();
    });

    it('should work independently without prior lockUI call', () => {
      // Should not throw errors when elements are already unlocked
      expect(() => unlockUI()).not.toThrow();

      const btn = document.getElementById('translate-btn');
      expect(btn.disabled).toBe(false);
    });
  });

  describe('Integration: lockUI/unlockUI cycle', () => {
    it('should maintain correct state through multiple lock/unlock cycles', () => {
      const btn = document.getElementById('translate-btn');

      // First cycle
      lockUI('first operation');
      expect(btn.disabled).toBe(true);
      expect(btn.getAttribute('aria-label')).toBe('Currently first operation...');

      unlockUI();
      expect(btn.disabled).toBe(false);
      expect(btn.getAttribute('aria-busy')).toBeNull();

      // Second cycle
      lockUI('second operation');
      expect(btn.disabled).toBe(true);
      expect(btn.getAttribute('aria-label')).toBe('Currently second operation...');

      unlockUI();
      expect(btn.disabled).toBe(false);
    });
  });
});
