/**
 * Upload Manager - AI Dubbing Studio
 *
 * Handles file upload with drag-and-drop support
 * Validates file type and size before processing
 */

/**
 * Upload Manager class
 */
export class UploadManager {
  constructor(dropZoneElement, fileInputElement, onFileSelect) {
    this.dropZone = dropZoneElement;
    this.fileInput = fileInputElement;
    this.onFileSelect = onFileSelect;
    this.selectedFile = null;

    // Allowed file extensions and MIME types
    this.validExtensions = ['.mp3', '.wav', '.ogg', '.m4a'];
    this.validMimeTypes = [
      'audio/mpeg',
      'audio/wav',
      'audio/ogg',
      'audio/x-m4a',
      'audio/mp4'
    ];
    this.maxSizeBytes = 25 * 1024 * 1024; // 25 MB

    this.init();
  }

  /**
   * Initialize upload functionality
   */
  init() {
    if (!this.dropZone || !this.fileInput) {
      console.error('Upload elements not found');
      return;
    }

    this.setupDragAndDrop();
    this.setupClickUpload();
    this.setupKeyboardSupport();
  }

  /**
   * Set up drag-and-drop functionality
   */
  setupDragAndDrop() {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      this.dropZone.addEventListener(eventName, this.preventDefaults, false);
      document.body.addEventListener(eventName, this.preventDefaults, false);
    });

    // Highlight drop zone when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
      this.dropZone.addEventListener(eventName, () => {
        this.dropZone.classList.add('upload-zone--dragging');
      }, false);
    });

    // Remove highlight when leaving or dropping
    ['dragleave', 'drop'].forEach(eventName => {
      this.dropZone.addEventListener(eventName, () => {
        this.dropZone.classList.remove('upload-zone--dragging');
      }, false);
    });

    // Handle dropped files
    this.dropZone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.handleFile(files[0]);
      }
    }, false);
  }

  /**
   * Set up click-to-upload functionality
   */
  setupClickUpload() {
    // Click on drop zone opens file picker
    this.dropZone.addEventListener('click', () => {
      this.fileInput.click();
    });

    // Handle file selection from picker
    this.fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        this.handleFile(e.target.files[0]);
      }
    });
  }

  /**
   * Set up keyboard navigation support
   */
  setupKeyboardSupport() {
    this.dropZone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.fileInput.click();
      }
    });
  }

  /**
   * Prevent default drag behaviors
   * @param {Event} e - Event object
   */
  preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  /**
   * Handle file selection
   * @param {File} file - Selected file
   * @returns {boolean} - True if valid, false otherwise
   */
  handleFile(file) {
    // Validate file
    const validation = this.validateFile(file);

    if (!validation.valid) {
      this.showError(validation.error);
      return false;
    }

    // Store file and trigger callback
    this.selectedFile = file;

    if (this.onFileSelect) {
      this.onFileSelect(file);
    }

    return true;
  }

  /**
   * Validate uploaded file
   * @param {File} file - File to validate
   * @returns {{valid: boolean, error?: string}} - Validation result
   */
  validateFile(file) {
    // Check file exists
    if (!file) {
      return {
        valid: false,
        error: 'No file selected'
      };
    }

    // Check file extension
    const fileName = file.name.toLowerCase();
    const hasValidExtension = this.validExtensions.some(ext =>
      fileName.endsWith(ext)
    );

    if (!hasValidExtension) {
      return {
        valid: false,
        error: `Invalid file type. Please upload an audio file: ${this.validExtensions.join(', ')}`
      };
    }

    // Check MIME type
    if (file.type && !this.validMimeTypes.includes(file.type)) {
      return {
        valid: false,
        error: `Invalid file format. Expected audio file, got: ${file.type}`
      };
    }

    // Check file size
    if (file.size > this.maxSizeBytes) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      const maxSizeMB = (this.maxSizeBytes / (1024 * 1024)).toFixed(0);
      return {
        valid: false,
        error: `File too large. Maximum size is ${maxSizeMB} MB. Your file is ${sizeMB} MB.`
      };
    }

    return { valid: true };
  }

  /**
   * Show error message (dispatches custom event)
   * @param {string} message - Error message
   */
  showError(message) {
    const event = new CustomEvent('upload-error', {
      detail: { message }
    });
    document.dispatchEvent(event);
  }

  /**
   * Reset upload state
   */
  reset() {
    this.selectedFile = null;
    this.fileInput.value = '';
    this.dropZone.classList.remove('upload-zone--dragging');
  }

  /**
   * Get selected file
   * @returns {File|null} - Selected file or null
   */
  getFile() {
    return this.selectedFile;
  }
}
