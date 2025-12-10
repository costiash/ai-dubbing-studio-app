/**
 * API Client - AI Dubbing Studio
 *
 * Handles all communication with the FastAPI backend
 * Base URL: http://localhost:8000
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * API Client class for backend communication
 */
export class APIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Check API health status
   * @returns {Promise<{status: string, openai_api_configured: boolean, version: string}>}
   */
  async healthCheck() {
    const response = await fetch(`${this.baseURL}/health`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }

  /**
   * Upload and transcribe audio file
   * @param {File} file - Audio file to transcribe
   * @param {string|null} language - Optional language code (e.g., 'en', 'he', 'ru')
   *                                  If null/empty, backend will auto-detect
   * @returns {Promise<{text: string, language: string}>}
   */
  async transcribeAudio(file, language = null) {
    const formData = new FormData();
    formData.append('file', file);

    // Add language parameter if provided
    if (language) {
      formData.append('language', language);
    }

    const response = await fetch(`${this.baseURL}/api/v1/audio/transcribe`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: 'Transcription failed'
      }));
      throw new Error(error.detail || 'Transcription failed');
    }

    return response.json();
  }

  /**
   * Translate text between languages
   * @param {string} text - Text to translate
   * @param {string} sourceLang - Source language name (e.g., "Hebrew")
   * @param {string} targetLang - Target language name (e.g., "Russian")
   * @returns {Promise<{translated_text: string, source_language: string, target_language: string}>}
   */
  async translateText(text, sourceLang, targetLang) {
    const response = await fetch(`${this.baseURL}/api/v1/audio/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        source_language: sourceLang,
        target_language: targetLang,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: 'Translation failed'
      }));
      throw new Error(error.detail || 'Translation failed');
    }

    return response.json();
  }

  /**
   * Generate speech from text (Text-to-Speech)
   * @param {string} text - Text to convert to speech
   * @param {string} voice - Voice name (default: "onyx")
   * @param {string} model - TTS model (default: "gpt-4o-mini-tts")
   * @param {string|null} instructions - Voice style instructions (only for gpt-4o-mini-tts)
   * @returns {Promise<Blob>} - MP3 audio blob
   */
  async generateTTS(text, voice = 'onyx', model = 'gpt-4o-mini-tts', instructions = null) {
    const payload = {
      text,
      voice,
      model,
    };

    // Only include instructions if provided and using gpt-4o-mini-tts
    if (instructions && model === 'gpt-4o-mini-tts') {
      payload.instructions = instructions;
    }

    const response = await fetch(`${this.baseURL}/api/v1/audio/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: 'TTS generation failed'
      }));
      throw new Error(error.detail || 'TTS generation failed');
    }

    return response.blob();
  }
}

// Export singleton instance
export const apiClient = new APIClient();
