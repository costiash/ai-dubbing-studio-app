/**
 * UI Feedback Manager
 *
 * Manages loading overlays, progress indicators, and error messages.
 * Single responsibility: User feedback during async operations.
 */
export class UIFeedbackManager {
  constructor() {
    this.loadingOverlay = document.getElementById('loading-overlay');
    this.loadingMessage = document.getElementById('loading-message');
    this.uploadProgress = document.getElementById('upload-progress');
    this.errorToast = document.getElementById('error-toast');
    this.errorMessage = document.getElementById('error-message');
  }

  /**
   * Show loading overlay with message
   * @param {string} message - Loading message to display
   */
  showLoading(message) {
    if (this.loadingOverlay) {
      this.loadingOverlay.classList.remove('hidden');
    }

    if (this.loadingMessage) {
      this.loadingMessage.textContent = message;
    }
  }

  /**
   * Hide loading overlay
   */
  hideLoading() {
    if (this.loadingOverlay) {
      this.loadingOverlay.classList.add('hidden');
    }
  }

  /**
   * Show upload progress indicator (indeterminate)
   */
  showUploadProgress() {
    if (this.uploadProgress) {
      this.uploadProgress.classList.remove('hidden');
      this.uploadProgress.classList.add('progress-bar--indeterminate');
    }
  }

  /**
   * Hide upload progress indicator
   */
  hideUploadProgress() {
    if (this.uploadProgress) {
      this.uploadProgress.classList.add('hidden');
      this.uploadProgress.classList.remove('progress-bar--indeterminate');
    }
  }

  /**
   * Show error toast message
   * @param {string} message - Error message to display
   */
  showError(message) {
    if (this.errorToast && this.errorMessage) {
      this.errorMessage.textContent = message;
      this.errorToast.classList.remove('hidden');

      // Auto-hide after 8 seconds
      setTimeout(() => {
        this.errorToast.classList.add('hidden');
      }, 8000);
    }

    console.error(message);
  }
}
