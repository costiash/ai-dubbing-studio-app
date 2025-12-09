import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { UIFeedbackManager } from '../../scripts/managers/UIFeedbackManager.js';

describe('UIFeedbackManager', () => {
  let manager;

  beforeEach(() => {
    // Set up DOM
    document.body.innerHTML = `
      <div id="loading-overlay" class="hidden"></div>
      <div id="loading-message"></div>
      <div id="upload-progress" class="hidden"></div>
      <div id="error-toast" class="hidden">
        <span id="error-message"></span>
      </div>
    `;

    // Mock console.error
    vi.spyOn(console, 'error').mockImplementation(() => {});

    // Create manager instance
    manager = new UIFeedbackManager();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Constructor', () => {
    it('should initialize with DOM element references', () => {
      expect(manager.loadingOverlay).toBeTruthy();
      expect(manager.loadingMessage).toBeTruthy();
      expect(manager.uploadProgress).toBeTruthy();
      expect(manager.errorToast).toBeTruthy();
      expect(manager.errorMessage).toBeTruthy();
    });

    it('should work with missing DOM elements', () => {
      document.body.innerHTML = '';
      expect(() => new UIFeedbackManager()).not.toThrow();
    });
  });

  describe('showLoading()', () => {
    it('should remove hidden class from loading overlay', () => {
      manager.showLoading('Test message');

      const overlay = document.getElementById('loading-overlay');
      expect(overlay.classList.contains('hidden')).toBe(false);
    });

    it('should set loading message text', () => {
      manager.showLoading('Processing data...');

      const message = document.getElementById('loading-message');
      expect(message.textContent).toBe('Processing data...');
    });

    it('should handle missing loading overlay gracefully', () => {
      manager.loadingOverlay = null;
      expect(() => manager.showLoading('Test')).not.toThrow();
    });

    it('should handle missing loading message gracefully', () => {
      manager.loadingMessage = null;
      expect(() => manager.showLoading('Test')).not.toThrow();
    });

    it('should update message on subsequent calls', () => {
      const message = document.getElementById('loading-message');

      manager.showLoading('First message');
      expect(message.textContent).toBe('First message');

      manager.showLoading('Second message');
      expect(message.textContent).toBe('Second message');
    });
  });

  describe('hideLoading()', () => {
    it('should add hidden class to loading overlay', () => {
      const overlay = document.getElementById('loading-overlay');
      overlay.classList.remove('hidden'); // Make it visible first

      manager.hideLoading();

      expect(overlay.classList.contains('hidden')).toBe(true);
    });

    it('should handle missing loading overlay gracefully', () => {
      manager.loadingOverlay = null;
      expect(() => manager.hideLoading()).not.toThrow();
    });

    it('should work when already hidden', () => {
      manager.hideLoading();
      expect(() => manager.hideLoading()).not.toThrow();
    });
  });

  describe('showUploadProgress()', () => {
    it('should remove hidden class from upload progress', () => {
      manager.showUploadProgress();

      const progress = document.getElementById('upload-progress');
      expect(progress.classList.contains('hidden')).toBe(false);
    });

    it('should add indeterminate class to progress bar', () => {
      manager.showUploadProgress();

      const progress = document.getElementById('upload-progress');
      expect(progress.classList.contains('progress-bar--indeterminate')).toBe(true);
    });

    it('should handle missing upload progress element gracefully', () => {
      manager.uploadProgress = null;
      expect(() => manager.showUploadProgress()).not.toThrow();
    });
  });

  describe('hideUploadProgress()', () => {
    it('should add hidden class to upload progress', () => {
      const progress = document.getElementById('upload-progress');
      progress.classList.remove('hidden'); // Make it visible first

      manager.hideUploadProgress();

      expect(progress.classList.contains('hidden')).toBe(true);
    });

    it('should remove indeterminate class from progress bar', () => {
      const progress = document.getElementById('upload-progress');
      progress.classList.add('progress-bar--indeterminate');

      manager.hideUploadProgress();

      expect(progress.classList.contains('progress-bar--indeterminate')).toBe(false);
    });

    it('should handle missing upload progress element gracefully', () => {
      manager.uploadProgress = null;
      expect(() => manager.hideUploadProgress()).not.toThrow();
    });
  });

  describe('showError()', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it('should set error message text', () => {
      manager.showError('Something went wrong');

      const message = document.getElementById('error-message');
      expect(message.textContent).toBe('Something went wrong');
    });

    it('should remove hidden class from error toast', () => {
      manager.showError('Error');

      const toast = document.getElementById('error-toast');
      expect(toast.classList.contains('hidden')).toBe(false);
    });

    it('should log error to console', () => {
      manager.showError('Test error');

      expect(console.error).toHaveBeenCalledWith('Test error');
    });

    it('should auto-hide error toast after 8 seconds', () => {
      const toast = document.getElementById('error-toast');

      manager.showError('Test error');
      expect(toast.classList.contains('hidden')).toBe(false);

      // Fast-forward time
      vi.advanceTimersByTime(8000);

      expect(toast.classList.contains('hidden')).toBe(true);
    });

    it('should not auto-hide before 8 seconds', () => {
      const toast = document.getElementById('error-toast');

      manager.showError('Test error');
      expect(toast.classList.contains('hidden')).toBe(false);

      // Fast-forward less than 8 seconds
      vi.advanceTimersByTime(5000);

      expect(toast.classList.contains('hidden')).toBe(false);
    });

    it('should handle missing error toast gracefully', () => {
      manager.errorToast = null;
      manager.errorMessage = null;

      expect(() => manager.showError('Test')).not.toThrow();
      expect(console.error).toHaveBeenCalledWith('Test');
    });

    it('should handle multiple errors', () => {
      const toast = document.getElementById('error-toast');
      const message = document.getElementById('error-message');

      manager.showError('First error');
      expect(message.textContent).toBe('First error');
      expect(toast.classList.contains('hidden')).toBe(false);

      manager.showError('Second error');
      expect(message.textContent).toBe('Second error');
      expect(toast.classList.contains('hidden')).toBe(false);

      // First error timer will fire after 8 seconds
      vi.advanceTimersByTime(8000);
      expect(toast.classList.contains('hidden')).toBe(true);
    });
  });

  describe('Integration: Loading workflow', () => {
    it('should support typical loading workflow', () => {
      const overlay = document.getElementById('loading-overlay');

      // Start loading
      manager.showLoading('Starting process...');
      expect(overlay.classList.contains('hidden')).toBe(false);

      // Update message
      manager.showLoading('Processing...');
      expect(overlay.classList.contains('hidden')).toBe(false);

      // Hide loading
      manager.hideLoading();
      expect(overlay.classList.contains('hidden')).toBe(true);
    });
  });

  describe('Integration: Upload progress workflow', () => {
    it('should support typical upload workflow', () => {
      const progress = document.getElementById('upload-progress');

      // Show progress
      manager.showUploadProgress();
      expect(progress.classList.contains('hidden')).toBe(false);
      expect(progress.classList.contains('progress-bar--indeterminate')).toBe(true);

      // Hide progress
      manager.hideUploadProgress();
      expect(progress.classList.contains('hidden')).toBe(true);
      expect(progress.classList.contains('progress-bar--indeterminate')).toBe(false);
    });
  });

  describe('Integration: Error display', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it('should display and auto-dismiss error', () => {
      const toast = document.getElementById('error-toast');
      const message = document.getElementById('error-message');

      manager.showError('Network error');

      expect(toast.classList.contains('hidden')).toBe(false);
      expect(message.textContent).toBe('Network error');

      vi.advanceTimersByTime(8000);

      expect(toast.classList.contains('hidden')).toBe(true);
    });
  });
});
