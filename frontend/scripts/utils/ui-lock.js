/**
 * UI Lock Utility
 *
 * Manages disabling/enabling interactive elements during async operations
 * to prevent duplicate submissions and provide accessibility feedback.
 */

/**
 * Disables all interactive elements during async operations
 * Prevents duplicate submissions and provides visual feedback
 * @param {string} operation - Name of operation for ARIA labels
 */
export function lockUI(operation = 'processing') {
  // Disable translate button
  const translateBtn = document.getElementById('translate-btn');
  if (translateBtn) {
    translateBtn.disabled = true;
    translateBtn.setAttribute('aria-busy', 'true');
    translateBtn.setAttribute('aria-label', `Currently ${operation}...`);
  }

  // Disable download button
  const downloadBtn = document.getElementById('download-btn');
  if (downloadBtn) {
    downloadBtn.disabled = true;
  }

  // Disable start new button
  const resetBtn = document.getElementById('start-new-btn');
  if (resetBtn) {
    resetBtn.disabled = true;
  }

  // Disable file upload
  const fileInput = document.getElementById('file-input');
  const dropZone = document.getElementById('upload-zone');
  if (fileInput) {
    fileInput.disabled = true;
  }
  if (dropZone) {
    dropZone.classList.add('upload-zone--disabled');
    dropZone.setAttribute('aria-disabled', 'true');
    dropZone.setAttribute('tabindex', '-1');
  }

  // Disable form selectors
  const sourceLangSelect = document.getElementById('source-language');
  const targetLangSelect = document.getElementById('target-language');
  const voiceSelect = document.getElementById('voice-select');
  const modelSelect = document.getElementById('model-select');
  [sourceLangSelect, targetLangSelect, voiceSelect, modelSelect].forEach(select => {
    if (select) {
      select.disabled = true;
    }
  });

  // Disable transcript editor
  const transcriptArea = document.getElementById('transcript-editor');
  if (transcriptArea) {
    transcriptArea.disabled = true;
  }
}

/**
 * Re-enables all interactive elements after async operations complete
 */
export function unlockUI() {
  // Enable translate button
  const translateBtn = document.getElementById('translate-btn');
  if (translateBtn) {
    translateBtn.disabled = false;
    translateBtn.removeAttribute('aria-busy');
    translateBtn.setAttribute('aria-label', 'Translate and generate audio');
  }

  // Enable download button
  const downloadBtn = document.getElementById('download-btn');
  if (downloadBtn) {
    downloadBtn.disabled = false;
  }

  // Enable start new button
  const resetBtn = document.getElementById('start-new-btn');
  if (resetBtn) {
    resetBtn.disabled = false;
  }

  // Enable file upload
  const fileInput = document.getElementById('file-input');
  const dropZone = document.getElementById('upload-zone');
  if (fileInput) {
    fileInput.disabled = false;
  }
  if (dropZone) {
    dropZone.classList.remove('upload-zone--disabled');
    dropZone.removeAttribute('aria-disabled');
    dropZone.setAttribute('tabindex', '0');
  }

  // Enable form selectors
  const sourceLangSelect = document.getElementById('source-language');
  const targetLangSelect = document.getElementById('target-language');
  const voiceSelect = document.getElementById('voice-select');
  const modelSelect = document.getElementById('model-select');
  [sourceLangSelect, targetLangSelect, voiceSelect, modelSelect].forEach(select => {
    if (select) {
      select.disabled = false;
    }
  });

  // Enable transcript editor
  const transcriptArea = document.getElementById('transcript-editor');
  if (transcriptArea) {
    transcriptArea.disabled = false;
  }
}
