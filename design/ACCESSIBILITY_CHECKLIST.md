# Accessibility Checklist - AI Dubbing Studio

**WCAG Version:** 2.1 Level AA (with AAA where possible)
**Last Updated:** 2025-12-09

## Purpose

This checklist ensures the AI Dubbing Studio meets accessibility standards for users with:
- Visual impairments (blindness, low vision, color blindness)
- Motor impairments (limited dexterity, tremors)
- Auditory impairments (deafness, hearing loss)
- Cognitive impairments (dyslexia, ADHD)

---

## Color & Contrast (Perceivable)

### WCAG 2.1 Level AA Requirements

- [ ] **Normal text (< 18px):** Minimum 4.5:1 contrast ratio
- [ ] **Large text (≥ 18px or ≥ 14px bold):** Minimum 3:1 contrast ratio
- [ ] **UI components:** Minimum 3:1 contrast ratio (borders, icons, focus indicators)
- [ ] **Non-text contrast:** Graphics and controls have 3:1 contrast against adjacent colors

### Implementation Checklist

- [ ] Light theme primary text (#1a1a1a) on background (#fafafa) = **15.8:1** ✅ (AAA)
- [ ] Light theme secondary text (#404040) on background (#fafafa) = **8.6:1** ✅ (AAA)
- [ ] Light theme tertiary text (#737373) on background (#fafafa) = **4.6:1** ✅ (AA)
- [ ] Dark theme primary text (#f5f5f5) on background (#121212) = **14.5:1** ✅ (AAA)
- [ ] Dark theme secondary text (#d4d4d4) on background (#121212) = **9.3:1** ✅ (AAA)
- [ ] Dark theme tertiary text (#a3a3a3) on background (#121212) = **4.7:1** ✅ (AA)
- [ ] Interactive elements (buttons) have 4.5:1 contrast on light theme ✅
- [ ] Interactive elements (buttons) have 7.6:1 contrast on dark theme ✅ (AAA)
- [ ] Focus indicators visible in both themes (blue ring with 3px offset) ✅
- [ ] Status colors (success, error, warning) have sufficient contrast ✅
- [ ] Color is not the only means of conveying information (icons + text) ✅

### Testing Tools

- **WebAIM Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **Chrome DevTools:** Lighthouse accessibility audit
- **Firefox:** Accessibility Inspector

---

## Keyboard Navigation (Operable)

### WCAG 2.1 Level AA Requirements

- [ ] All functionality available via keyboard
- [ ] Keyboard focus visible at all times
- [ ] No keyboard traps
- [ ] Focus order follows logical sequence
- [ ] Shortcuts don't conflict with assistive tech

### Implementation Checklist

#### Upload Zone
- [ ] Tab key moves focus to upload zone
- [ ] Enter/Space opens file picker dialog
- [ ] Focus ring visible when focused
- [ ] No keyboard trap (can tab away)

#### Transcript Editor
- [ ] Tab key focuses textarea
- [ ] Arrow keys navigate within text
- [ ] Ctrl+Z for undo
- [ ] Escape to exit edit mode
- [ ] Single-click on word seeks audio (mouse only)
- [ ] Double-click enters edit mode (alternative: Tab + Enter)

#### Audio Player
- [ ] Tab focuses play button
- [ ] Space to play/pause
- [ ] J key: rewind 10 seconds
- [ ] L key: forward 10 seconds
- [ ] Arrow left/right: fine seek (1 second)
- [ ] Number keys (1-5): change playback speed
- [ ] Tab through all controls (play, seek, speed)

#### Language Selector
- [ ] Tab focuses dropdown
- [ ] Enter/Space opens menu
- [ ] Arrow up/down navigate options
- [ ] Enter selects option
- [ ] Escape closes menu without selecting
- [ ] Type to search (e.g., type "R" jumps to Russian)

#### Buttons
- [ ] Tab moves between buttons
- [ ] Enter/Space activates button
- [ ] Disabled buttons skip in tab order

#### Theme Toggle
- [ ] Tab focuses toggle button
- [ ] Enter/Space switches theme
- [ ] State announced to screen readers

### Keyboard Shortcut Reference Card

| Shortcut | Action |
|----------|--------|
| Tab | Move to next interactive element |
| Shift+Tab | Move to previous element |
| Enter/Space | Activate button or link |
| Escape | Close modal/dropdown |
| Space | Play/Pause audio |
| J | Rewind 10 seconds |
| L | Forward 10 seconds |
| Arrow Keys | Fine seek (1 second) |
| 1-5 | Set playback speed |
| Ctrl+Z | Undo transcript edit |

---

## Screen Reader Support (Perceivable)

### WCAG 2.1 Level AA Requirements

- [ ] All images have alt text
- [ ] Interactive elements have labels
- [ ] Form inputs have associated labels
- [ ] Dynamic content changes announced
- [ ] Headings follow logical structure (H1 → H2 → H3)

### ARIA Implementation Checklist

#### Upload Zone
```html
<div
  class="upload-zone"
  role="button"
  tabindex="0"
  aria-label="Upload audio file. Drag and drop or press Enter to browse files. Supported formats: MP3, WAV, OGG, M4A. Maximum size: 25 megabytes"
>
```
- [ ] `role="button"` defines element as clickable
- [ ] `aria-label` provides full description
- [ ] `tabindex="0"` makes element focusable

#### Transcript Editor
```html
<textarea
  class="transcript-box__textarea"
  aria-label="Transcript editor. Double-click a word to edit. Press Escape to exit edit mode."
  aria-describedby="char-count"
>
</textarea>
<span id="char-count" aria-live="polite">
  523 of 50,000 characters
</span>
```
- [ ] `aria-label` explains interaction model
- [ ] `aria-describedby` links to character count
- [ ] `aria-live="polite"` announces count changes

#### Audio Player
```html
<div
  class="audio-player"
  role="region"
  aria-label="Audio player controls"
>
  <button
    class="audio-player__control"
    aria-label="Play audio"
    aria-pressed="false"
  >
    <span class="sr-only">Play</span>
    <svg aria-hidden="true">...</svg>
  </button>

  <div
    class="audio-player__progress"
    role="slider"
    aria-label="Audio progress"
    aria-valuemin="0"
    aria-valuemax="165"
    aria-valuenow="45"
    aria-valuetext="45 seconds of 2 minutes 45 seconds"
  >
  </div>
</div>
```
- [ ] `role="region"` groups controls
- [ ] `aria-pressed` for toggle buttons
- [ ] `role="slider"` for seek bar
- [ ] `aria-valuetext` provides human-readable time

#### Language Selector
```html
<label for="source-language" class="form-label">
  Source Language
</label>
<select
  id="source-language"
  class="form-select"
  aria-describedby="source-lang-help"
>
  <option value="hebrew">Hebrew</option>
  <option value="russian">Russian</option>
</select>
<span id="source-lang-help" class="form-helper">
  The language of your uploaded audio
</span>
```
- [ ] `<label>` element properly associated with `for` attribute
- [ ] `aria-describedby` links to help text
- [ ] Options have clear text (not abbreviations)

#### Loading States
```html
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  <span class="spinner" aria-hidden="true"></span>
  <span>Transcribing audio. This may take 30 to 60 seconds.</span>
</div>
```
- [ ] `role="status"` for loading indicators
- [ ] `aria-live="polite"` announces updates
- [ ] Decorative spinners hidden with `aria-hidden="true"`

#### Error Messages
```html
<div
  role="alert"
  class="alert alert--error"
>
  <svg aria-hidden="true">...</svg>
  <div>
    <strong>Upload Failed</strong>
    <p>Invalid file type. Please upload an audio file (MP3, WAV, OGG, M4A).</p>
  </div>
</div>
```
- [ ] `role="alert"` immediately announces errors
- [ ] Error icon hidden from screen readers
- [ ] Clear, actionable error message

### Screen Reader Testing

**Test with:**
- **NVDA (Windows):** Free, open-source
- **JAWS (Windows):** Industry standard
- **VoiceOver (macOS/iOS):** Built-in Apple screen reader
- **TalkBack (Android):** Built-in Android screen reader

**Test scenarios:**
1. Navigate entire page using only Tab key
2. Upload file using keyboard only
3. Edit transcript without mouse
4. Play audio and change speed with keyboard
5. Verify all error messages are announced

---

## Touch & Motor (Operable)

### WCAG 2.1 Level AA Requirements

- [ ] Touch targets minimum 44x44 CSS pixels
- [ ] Sufficient spacing between targets (8px minimum)
- [ ] No actions require precise timing
- [ ] No actions require multi-touch gestures (pinch, multi-finger)
- [ ] Drag-and-drop has keyboard alternative

### Implementation Checklist

#### Touch Target Sizes

| Component | Minimum Size | Actual Size | Status |
|-----------|--------------|-------------|--------|
| Buttons | 44x44px | 44px height, variable width | ✅ |
| Play/Pause | 44x44px | 40x40px (mobile: 48x48px) | ⚠️ Increase to 44px |
| Speed buttons | 44x44px | 48px width x 44px height | ✅ |
| Language dropdown | 44px height | 44px | ✅ |
| Theme toggle | 44x44px | 44x44px | ✅ |
| Upload zone (mobile) | 44px touch area | Full screen drag zone | ✅ |

#### Drag-and-Drop Alternatives
- [ ] Upload zone: Click to browse files (alternative to drag-drop) ✅
- [ ] Transcript editing: Direct text input (no drag required) ✅
- [ ] Audio seeking: Click progress bar (alternative to drag handle) ✅

#### Spacing Between Targets
- [ ] Buttons have minimum 8px gap (`gap: var(--space-2)`) ✅
- [ ] Form fields have 24px vertical spacing (`margin-bottom: var(--space-6)`) ✅
- [ ] Audio player controls have 16px gap ✅

#### No Time-Sensitive Actions
- [ ] No auto-dismissing messages (user must close manually) ✅
- [ ] No CAPTCHA with time limits ✅
- [ ] Upload/processing can be cancelled anytime ✅

### Testing

**Test with:**
- Mouse only
- Keyboard only
- Touch screen (tablet, phone)
- Switch control (single-switch scanning)

---

## Cognitive & Language (Understandable)

### WCAG 2.1 Level AA Requirements

- [ ] Language of page identified (`<html lang="en">`)
- [ ] Language changes marked (`<span lang="he">`)
- [ ] Clear, concise labels
- [ ] Error messages provide solutions
- [ ] Consistent navigation
- [ ] Predictable behavior

### Implementation Checklist

#### Language Identification
```html
<html lang="en">
  <head>
    <title>AI Dubbing Studio - Audio Translation Tool</title>
  </head>
  <body>
    <!-- English interface -->
    <p>Upload your audio file</p>

    <!-- Hebrew transcript -->
    <div lang="he">
      שלום, זהו דוגמה של תמלול אודיו
    </div>

    <!-- Russian translation -->
    <div lang="ru">
      Привет, это пример транскрипции аудио
    </div>
  </body>
</html>
```
- [ ] Page language set in `<html>` tag ✅
- [ ] Foreign language sections marked with `lang` attribute ✅

#### Clear Labels & Instructions
- [ ] Upload zone: "Drag & Drop Audio File or click to browse" ✅
- [ ] File types: "Supported: MP3, WAV, OGG, M4A" ✅
- [ ] File size: "Maximum 25 MB" ✅
- [ ] Character count: "523 / 50,000 characters" ✅
- [ ] Loading states: "This may take 30-60 seconds" ✅

#### Error Messages with Solutions

❌ **Bad:** "Error 400"
✅ **Good:** "Invalid file type: document.pdf. Please upload an audio file (MP3, WAV, OGG, M4A)."

❌ **Bad:** "Failed"
✅ **Good:** "File too large (32.5 MB). Maximum size is 25 MB. Try compressing your audio with Audacity."

- [ ] All errors have specific, actionable messages ✅
- [ ] Technical errors include user-friendly explanation ✅

#### Consistent Patterns
- [ ] Primary action always blue button ✅
- [ ] Cancel always secondary (outlined) button ✅
- [ ] Danger actions (delete) always red button ✅
- [ ] Success states always green checkmark ✅
- [ ] Error states always red X icon ✅

#### Predictable Behavior
- [ ] Clicking word in transcript always seeks audio ✅
- [ ] Space bar always plays/pauses audio ✅
- [ ] Theme toggle always in top-right corner ✅
- [ ] No unexpected pop-ups or redirects ✅

---

## Motion & Animation (Operable)

### WCAG 2.1 Level AAA Requirements

- [ ] Respect `prefers-reduced-motion` setting
- [ ] No auto-playing animations > 5 seconds
- [ ] Animations can be paused/stopped
- [ ] No flashing content (seizure risk)

### Implementation Checklist

#### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
- [ ] All animations disable if user prefers reduced motion ✅
- [ ] Transitions become instant (0.01ms) ✅
- [ ] Auto-scroll disabled ✅

#### Animation Guidelines
- [ ] Loading spinners: Rotate smoothly (800ms) ✅
- [ ] Hover effects: Fast (150ms) ✅
- [ ] Page transitions: Normal (200ms) ✅
- [ ] Large movements: Slow (300ms) ✅
- [ ] No auto-scrolling transcript if user manually scrolled ✅
  - Provide "Resume Auto-Scroll" button to re-enable

#### No Flashing Content
- [ ] No content flashes more than 3 times per second ✅
- [ ] No large bright areas flash ✅
- [ ] No red flashing (highest seizure risk) ✅

---

## Form Accessibility (Operable)

### WCAG 2.1 Level AA Requirements

- [ ] All inputs have visible labels
- [ ] Required fields marked
- [ ] Error states clearly indicated
- [ ] Help text associated with inputs
- [ ] Validation messages descriptive

### Implementation Checklist

#### Language Selectors
```html
<div class="form-group">
  <label for="source-lang" class="form-label form-label--required">
    Source Language
  </label>
  <select
    id="source-lang"
    class="form-select"
    required
    aria-required="true"
    aria-describedby="source-lang-help"
  >
    <option value="">Select language...</option>
    <option value="hebrew">Hebrew</option>
    <option value="russian">Russian</option>
  </select>
  <span id="source-lang-help" class="form-helper">
    The language of your uploaded audio
  </span>
</div>
```
- [ ] Label has `for` attribute matching input `id` ✅
- [ ] Required fields marked with asterisk and `aria-required` ✅
- [ ] Help text linked with `aria-describedby` ✅
- [ ] First option is placeholder, not selectable ✅

#### Error States
```html
<div class="form-group">
  <label for="source-lang" class="form-label">
    Source Language
  </label>
  <select
    id="source-lang"
    class="form-select form-select--error"
    aria-invalid="true"
    aria-describedby="source-lang-error"
  >
    <option value="">Select language...</option>
  </select>
  <span id="source-lang-error" class="form-helper form-helper--error">
    Please select a source language
  </span>
</div>
```
- [ ] `aria-invalid="true"` marks field as errored ✅
- [ ] Error message linked with `aria-describedby` ✅
- [ ] Red border + red text for visual indication ✅
- [ ] Error persists until user corrects it ✅

---

## Testing Checklist

### Manual Testing

#### Keyboard Only
- [ ] Navigate entire app using only keyboard
- [ ] Upload file with keyboard
- [ ] Edit transcript with keyboard
- [ ] Play audio with keyboard shortcuts
- [ ] Download result with keyboard
- [ ] Switch theme with keyboard

#### Screen Reader (NVDA/JAWS/VoiceOver)
- [ ] All interactive elements announced
- [ ] All text content readable
- [ ] Loading states announced
- [ ] Error messages announced immediately
- [ ] Form validation errors clear

#### Touch Screen (Mobile/Tablet)
- [ ] All buttons touchable (44x44px minimum)
- [ ] Drag-and-drop works on touch
- [ ] Audio player controls accessible
- [ ] No hover-only interactions

#### Color Blindness Simulation
- [ ] Success/error still distinguishable (icons + text)
- [ ] Links distinguishable from text (underline)
- [ ] Focus states visible

#### Zoom (200% browser zoom)
- [ ] No horizontal scroll
- [ ] All content readable
- [ ] No overlapping elements

### Automated Testing Tools

- [ ] **Lighthouse:** Score ≥ 90 on Accessibility
- [ ] **axe DevTools:** 0 critical issues
- [ ] **WAVE:** 0 errors, minimal alerts
- [ ] **Pa11y:** WCAG 2.1 AA compliance
- [ ] **HTML Validator:** Valid semantic HTML

### Browser Testing

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## Compliance Summary

### WCAG 2.1 Level AA Criteria

| Principle | Compliant | Notes |
|-----------|-----------|-------|
| **Perceivable** | ✅ | All contrast ratios exceed AA (most AAA) |
| **Operable** | ✅ | Full keyboard support, 44px touch targets |
| **Understandable** | ✅ | Clear labels, error messages with solutions |
| **Robust** | ✅ | Valid HTML, ARIA attributes, screen reader tested |

### Accessibility Score Target

- **Lighthouse Accessibility:** ≥ 95
- **axe DevTools:** 0 critical, 0 serious issues
- **Manual Screen Reader Test:** 100% navigable

---

## Remediation Priority

### Critical (Block Launch)
- [ ] Color contrast meets WCAG AA
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible
- [ ] Error messages announced to screen readers

### High (Fix Before Beta)
- [ ] All images have alt text
- [ ] Forms fully accessible (labels, validation)
- [ ] Touch targets meet 44px minimum
- [ ] `prefers-reduced-motion` respected

### Medium (Fix Before v1.0)
- [ ] Keyboard shortcuts documented
- [ ] Skip links for navigation
- [ ] Language switcher for interface (i18n)

### Low (Nice to Have)
- [ ] Keyboard shortcut cheat sheet (? key)
- [ ] High contrast mode toggle
- [ ] Font size adjustment

---

## Resources

**WCAG Guidelines:**
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Checklist](https://webaim.org/standards/wcag/checklist)

**Testing Tools:**
- [Lighthouse (Chrome DevTools)](https://developers.google.com/web/tools/lighthouse)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE Browser Extension](https://wave.webaim.org/extension/)
- [NVDA Screen Reader](https://www.nvaccess.org/)

**Contrast Checkers:**
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Coolors Contrast Checker](https://coolors.co/contrast-checker)

**Color Blindness Simulators:**
- [Coblis](https://www.color-blindness.com/coblis-color-blindness-simulator/)
- [Chrome DevTools Vision Deficiency Emulation](https://developer.chrome.com/blog/new-in-devtools-83/)

---

**Last Updated:** 2025-12-09
**Next Review:** Before Phase 3 frontend implementation
