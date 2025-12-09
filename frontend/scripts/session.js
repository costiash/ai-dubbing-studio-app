/**
 * Session Manager - AI Dubbing Studio
 *
 * Manages session state persistence using localStorage
 * Allows users to restore their work if they refresh the page
 */

/**
 * Session Manager class
 */
export class SessionManager {
  constructor() {
    this.sessionId = this.getOrCreateSessionId();
    this.storageKey = `dubbing_session_${this.sessionId}`;
  }

  /**
   * Get or create a unique session ID
   * @returns {string} - Session ID
   */
  getOrCreateSessionId() {
    let id = localStorage.getItem('dubbing_session_id');

    if (!id) {
      id = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('dubbing_session_id', id);
    }

    return id;
  }

  /**
   * Save a value to session state
   * @param {string} key - State key
   * @param {any} value - Value to save
   */
  saveState(key, value) {
    const state = this.getState();
    state[key] = value;
    state.lastUpdated = Date.now();

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(state));
    } catch (error) {
      console.warn('Failed to save session state:', error);
    }
  }

  /**
   * Get entire session state
   * @returns {Object} - Session state object
   */
  getState() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.warn('Failed to load session state:', error);
      return {};
    }
  }

  /**
   * Get a specific value from session state
   * @param {string} key - State key
   * @param {any} defaultValue - Default value if key doesn't exist
   * @returns {any} - Stored value or default
   */
  getValue(key, defaultValue = null) {
    const state = this.getState();
    return state[key] !== undefined ? state[key] : defaultValue;
  }

  /**
   * Clear entire session state
   */
  clearState() {
    try {
      localStorage.removeItem(this.storageKey);
    } catch (error) {
      console.warn('Failed to clear session state:', error);
    }
  }

  /**
   * Clear a specific key from session state
   * @param {string} key - State key to remove
   */
  clearValue(key) {
    const state = this.getState();
    delete state[key];

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(state));
    } catch (error) {
      console.warn('Failed to clear session value:', error);
    }
  }

  /**
   * Check if session has data
   * @returns {boolean} - True if session has saved state
   */
  hasState() {
    const state = this.getState();
    return Object.keys(state).length > 0;
  }

  /**
   * Get session age in milliseconds
   * @returns {number} - Age in milliseconds, or 0 if no session
   */
  getSessionAge() {
    const state = this.getState();
    if (state.lastUpdated) {
      return Date.now() - state.lastUpdated;
    }
    return 0;
  }
}

// Export singleton instance
export const sessionManager = new SessionManager();
