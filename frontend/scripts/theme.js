/**
 * Theme Manager - AI Dubbing Studio
 *
 * Manages Dark/Light theme switching with OS preference detection
 * Persists user preference to localStorage
 */

/**
 * Theme Manager class
 */
export class ThemeManager {
  constructor() {
    this.themeToggle = null;
    this.currentTheme = this.getInitialTheme();
  }

  /**
   * Initialize theme system
   * Sets up event listeners and applies initial theme
   */
  init() {
    this.themeToggle = document.getElementById('theme-toggle');

    if (!this.themeToggle) {
      console.warn('Theme toggle button not found');
      return;
    }

    // Apply initial theme
    this.applyTheme(this.currentTheme);

    // Set up toggle click handler
    this.themeToggle.addEventListener('click', () => this.toggle());

    // Keyboard support (Enter/Space)
    this.themeToggle.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.toggle();
      }
    });

    // Listen for OS preference changes
    this.setupMediaQueryListener();
  }

  /**
   * Get initial theme (localStorage or system preference)
   * @returns {string} - 'light' or 'dark'
   */
  getInitialTheme() {
    // Check localStorage first
    const saved = localStorage.getItem('theme');
    if (saved === 'light' || saved === 'dark') {
      return saved;
    }

    // Fall back to system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  /**
   * Apply theme to document
   * @param {string} theme - 'light' or 'dark'
   */
  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    this.currentTheme = theme;
    localStorage.setItem('theme', theme);

    // Update ARIA state on toggle button
    if (this.themeToggle) {
      this.themeToggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
      this.themeToggle.setAttribute(
        'aria-label',
        theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
      );
    }
  }

  /**
   * Toggle between light and dark themes
   */
  toggle() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
  }

  /**
   * Listen for system theme preference changes
   */
  setupMediaQueryListener() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    // Only auto-switch if user hasn't explicitly set a preference
    mediaQuery.addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        this.applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  /**
   * Get current theme
   * @returns {string} - 'light' or 'dark'
   */
  getTheme() {
    return this.currentTheme;
  }
}

// Export singleton instance
export const themeManager = new ThemeManager();
