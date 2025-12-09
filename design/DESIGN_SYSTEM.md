# Design System - AI Dubbing Studio

**Version:** 1.0
**Date:** 2025-12-09
**Status:** Phase 2 Complete - Ready for Frontend Implementation

## Table of Contents

- [Design Philosophy](#design-philosophy)
- [Color System](#color-system)
- [Typography](#typography)
- [Spacing System](#spacing-system)
- [Component Specifications](#component-specifications)
- [Responsive Design](#responsive-design)
- [Animation Guidelines](#animation-guidelines)
- [Accessibility](#accessibility)

---

## Design Philosophy

### Core Principles

**"Immersive Interactive Transcripts"** - Text becomes the controller

The AI Dubbing Studio breaks away from static "player + text" layouts. Our design philosophy centers on making the transcript the primary interaction surface, where text synchronizes with audio playback in real-time using karaoke-style highlighting.

#### Key Design Tenets

1. **Clarity Over Cleverness** - Users understand instantly without tutorials
2. **Kinetic Feedback** - Motion confirms actions (drag-and-drop zones react to the entire viewport)
3. **Progressive Disclosure** - Complexity reveals gradually (basic upload → transcribe → edit → translate → generate)
4. **Accessibility First** - Keyboard navigation, screen readers, and high contrast are requirements, not afterthoughts
5. **Performance Is UX** - Animations respect `prefers-reduced-motion`, all interactions respond within 100ms

### Inspiration & Research

Based on analysis of modern audio tools:
- **Descript** - Click-to-seek transcript editing
- **Otter.ai** - Real-time synchronized highlighting
- **Trint** - Collaborative editing with confidence scoring
- **FigJam/Miro** - Kinetic drop zones that respond to viewport-level events

Research sources:
- [15 Drag and Drop UI Design Tips - Bricx Labs](https://bricxlabs.com/blogs/drag-and-drop-ui)
- [Designing Drag and Drop UIs - LogRocket Blog](https://blog.logrocket.com/ux-design/drag-and-drop-ui-examples/)
- Gemini AI consultation on 2025 UX best practices

---

## Color System

### Philosophy

**Dark Grey, Not Pure Black** - Reduces OLED screen burn-in and eye strain
**Off-White, Not Pure White** - Softer on eyes during long editing sessions
**Blue for Interactivity** - Universal, accessible, familiar

### Light Theme Palette

| Token | Hex | Usage | Contrast Ratio |
|-------|-----|-------|----------------|
| `--theme-surface-1` | `#fafafa` | Primary background | Base |
| `--theme-surface-2` | `#f5f5f5` | Secondary areas | Base |
| `--theme-surface-elevated` | `#ffffff` | Cards, modals | Base |
| `--theme-text-1` | `#1a1a1a` | Primary text | **15.8:1** (AAA) |
| `--theme-text-2` | `#404040` | Secondary text | **8.6:1** (AAA) |
| `--theme-text-3` | `#737373` | Tertiary text | **4.6:1** (AA) |
| `--theme-accent` | `#2563eb` | Interactive elements | **4.5:1** on white (AA) |
| `--theme-border-1` | `#e5e5e5` | Primary borders | Subtle |

**Rationale:**
- Off-white (#fafafa) instead of pure white reduces glare
- Dark grey (#1a1a1a) instead of pure black is easier to read
- Blue (#2563eb) is universally recognized as "interactive"
- All text colors exceed WCAG 2.1 AA minimum (4.5:1)

### Dark Theme Palette

| Token | Hex | Usage | Contrast Ratio |
|-------|-----|-------|----------------|
| `--theme-surface-1` | `#121212` | Primary background | Base |
| `--theme-surface-2` | `#1e1e1e` | Secondary areas | Base |
| `--theme-surface-elevated` | `#2d2d2d` | Cards, modals | Base |
| `--theme-text-1` | `#f5f5f5` | Primary text | **14.5:1** (AAA) |
| `--theme-text-2` | `#d4d4d4` | Secondary text | **9.3:1** (AAA) |
| `--theme-text-3` | `#a3a3a3` | Tertiary text | **4.7:1** (AA) |
| `--theme-accent` | `#60a5fa` | Interactive elements | **7.6:1** on dark (AAA) |
| `--theme-border-1` | `#3a3a3a` | Primary borders | Subtle |

**Rationale:**
- Dark grey (#121212) instead of pure black (#000000) prevents OLED smearing
- Lighter blue (#60a5fa) maintains visibility on dark backgrounds
- All text exceeds WCAG 2.1 AA standards

### Semantic Status Colors

**Consistent across themes** - Colors have intrinsic meaning

| Status | Light Bg | Dark Bg | Border | Meaning |
|--------|----------|---------|--------|---------|
| Success | `#d1fae5` | `#064e3b` | `#10b981` | Operation completed |
| Warning | `#fef3c7` | `#78350f` | `#f59e0b` | Attention needed |
| Error | `#fee2e2` | `#7f1d1d` | `#ef4444` | Failed or blocked |
| Info | `#dbeafe` | `#1e3a8a` | `#3b82f6` | Informational |

**Usage:**
- Success: File uploaded, transcription complete
- Warning: Low-confidence words, approaching character limit
- Error: Upload failed, API error
- Info: Tips, keyboard shortcuts

### Audio-Specific Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--color-audio-waveform` | `var(--theme-accent)` | Waveform visualization |
| `--color-audio-progress` | `var(--theme-accent-hover)` | Playback position |
| `--color-audio-highlight` | `var(--theme-accent)` | Active word (karaoke) |
| `--transcript-low-confidence` | `#f59e0b` (amber) | Uncertain AI transcription |

---

## Typography

### Font Stack

**Primary Font: Inter**
- Clean, neutral, highly readable at small sizes
- Excellent screen rendering across devices
- Wide language support (Hebrew, Russian, English)

**Display Font: Space Grotesk**
- Used for headings and hero text
- Modern, slightly playful without being unprofessional

**Monospace Font: JetBrains Mono**
- Code-like elements (timestamps, character counts)
- Clear distinction between regular and monospace text

```css
--font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-family-display: 'Space Grotesk', 'Inter', sans-serif;
--font-family-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### Type Scale (Major Third: 1.25 ratio)

| Class | Size | Pixels | Usage |
|-------|------|--------|-------|
| `--font-size-xs` | 0.64rem | 10px | Fine print, metadata |
| `--font-size-sm` | 0.8rem | 13px | Helper text, labels |
| `--font-size-base` | 1rem | 16px | Body text (default) |
| `--font-size-md` | 1.125rem | 18px | Emphasized body |
| `--font-size-lg` | 1.25rem | 20px | Subheadings |
| `--font-size-xl` | 1.563rem | 25px | Section headings |
| `--font-size-2xl` | 1.953rem | 31px | Page titles |
| `--font-size-3xl` | 2.441rem | 39px | Hero headings |
| `--font-size-4xl` | 3.052rem | 49px | Marketing headers |

**Rationale:**
- Major Third (1.25) creates visual hierarchy without excessive size jumps
- Base size of 16px ensures readability on all devices
- Avoids intermediate sizes that cause inconsistency

### Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Normal | 400 | Body text, descriptions |
| Medium | 500 | Button labels, emphasized text |
| Semibold | 600 | Section headings, labels |
| Bold | 700 | Page titles, strong emphasis |

**Usage Guidelines:**
- Use **normal (400)** for body text
- Use **medium (500)** for button labels
- Use **semibold (600)** for card titles, form labels
- Use **bold (700)** sparingly for primary headings only

### Line Height

| Token | Value | Usage |
|-------|-------|-------|
| `--line-height-tight` | 1.25 | Headings, single-line elements |
| `--line-height-normal` | 1.5 | Body text, paragraphs |
| `--line-height-relaxed` | 1.75 | Long-form content, transcripts |

**Rationale:**
- Tight (1.25) prevents headings from feeling disconnected
- Normal (1.5) balances readability and density
- Relaxed (1.75) improves comprehension in long transcripts

### Letter Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `--letter-spacing-tight` | -0.02em | Large headings (optical correction) |
| `--letter-spacing-normal` | 0 | Default |
| `--letter-spacing-wide` | 0.025em | Uppercase labels |
| `--letter-spacing-wider` | 0.05em | All-caps section titles |

---

## Spacing System

### 8px Grid System

All spacing uses multiples of 4px for consistency and mathematical harmony.

```
Base unit: 4px
Grid: 8px (2x base)
```

| Token | Rem | Pixels | Usage |
|-------|-----|--------|-------|
| `--space-0` | 0 | 0px | No spacing |
| `--space-1` | 0.25rem | 4px | Tight gaps, borders |
| `--space-2` | 0.5rem | 8px | Small padding |
| `--space-3` | 0.75rem | 12px | Compact elements |
| `--space-4` | 1rem | 16px | **Standard padding** |
| `--space-5` | 1.25rem | 20px | Medium gaps |
| `--space-6` | 1.5rem | 24px | **Section spacing** |
| `--space-8` | 2rem | 32px | Large spacing |
| `--space-10` | 2.5rem | 40px | XL spacing |
| `--space-12` | 3rem | 48px | XXL spacing |
| `--space-16` | 4rem | 64px | Section dividers |
| `--space-20` | 5rem | 80px | Major sections |

### Layout Patterns

**Stack Layout** (Vertical spacing):
```css
.stack > * + * {
  margin-top: var(--space-6); /* 24px between sections */
}
```

**Inline Layout** (Horizontal spacing):
```css
.inline {
  display: flex;
  gap: var(--space-4); /* 16px between items */
}
```

**Card Padding**:
- Small cards: `var(--space-4)` (16px)
- Standard cards: `var(--space-6)` (24px)
- Large cards: `var(--space-8)` (32px)

---

## Component Specifications

### 1. Upload Zone Component

**Purpose:** Drag-and-drop file upload with kinetic feedback

#### States

| State | Visual Treatment | Trigger |
|-------|------------------|---------|
| **Default** | Dashed border, muted icon | Initial render |
| **Hover** | Solid border, highlighted icon, slight scale | Mouse over |
| **Dragging** | Bright background, thick border, scale up | File dragged over |
| **Uploading** | Progress bar, spinner | File processing |
| **Success** | Green checkmark, fade out | Upload complete |
| **Error** | Red border, error icon, message | Upload failed |

#### Visual Specifications

```css
/* Default */
background: var(--color-surface-secondary);
border: 2px dashed var(--color-border-primary);
border-radius: var(--radius-xl); /* 16px */
min-height: 200px;
padding: var(--space-8); /* 32px */

/* Dragging (kinetic reaction) */
background: var(--theme-accent-transparent); /* 20% opacity blue */
border: 3px dashed var(--color-interactive);
transform: scale(1.02);
box-shadow: var(--shadow-lg);
```

#### Content Structure

```
┌─────────────────────────────────────┐
│          [Upload Icon]              │
│         48x48px, centered           │
│                                     │
│  "Drag & Drop Audio File"          │
│  (font-size-lg, semibold)          │
│                                     │
│  "or click to browse"               │
│  (font-size-sm, secondary)         │
│                                     │
│  "Supported: MP3, WAV, OGG, M4A"   │
│  (font-size-xs, tertiary)          │
└─────────────────────────────────────┘
```

#### Accessibility

- **ARIA:** `role="button"` `aria-label="Upload audio file. Drag and drop or press enter to browse"`
- **Keyboard:** Enter/Space to open file picker
- **Screen Reader:** Announces "Upload zone. Drag and drop or press enter to browse files. Supported formats: MP3, WAV, OGG, M4A"
- **Focus:** Clear focus ring (`box-shadow: var(--shadow-focus)`)

#### Validation

- **File Types:** `.mp3, .wav, .ogg, .m4a` (case-insensitive)
- **Max Size:** 25 MB (OpenAI limit)
- **Error Feedback:** Alert banner with specific error message

---

### 2. Transcript Editor Component

**Purpose:** Editable text area with synchronized playback highlighting

#### Features

1. **Karaoke-Style Highlighting**
   - Active word: bright blue background, white text
   - Synced with audio playback
   - Auto-scrolls to keep active word centered

2. **Low-Confidence Indicators**
   - Words with <80% AI confidence: amber dotted underline
   - Tooltip on hover: "Low confidence - verify accuracy"

3. **Click-to-Seek**
   - Single click on word: seeks audio to that timestamp
   - Double click: enters edit mode for that word

#### Visual Specifications

```css
/* Container */
background: var(--color-surface-primary);
border: 1px solid var(--color-border-primary);
border-radius: var(--radius-lg); /* 12px */
padding: var(--space-6); /* 24px */
min-height: 200px;
box-shadow: var(--shadow-sm);

/* Active word (karaoke) */
.word--active {
  background: var(--theme-accent);
  color: var(--theme-text-inverse);
  padding: 2px 4px;
  border-radius: 4px;
  animation: pulse-highlight 200ms ease-in-out;
}

/* Low confidence */
.word--low-confidence {
  border-bottom: 2px dotted #f59e0b;
  cursor: help;
}
```

#### Character Count

- **Position:** Bottom-right corner, absolute positioned
- **Display:** `{current} / {max}` in monospace font
- **Colors:**
  - Normal: `var(--color-text-tertiary)`
  - Warning (>90%): `var(--color-warning)`
  - Error (>100%): `var(--color-error)`

#### Accessibility

- **ARIA:** `role="textbox"` `aria-multiline="true"` `aria-label="Transcript editor"`
- **Keyboard:** Tab to focus, Ctrl+Z for undo
- **Screen Reader:** Announces character count changes
- **Auto-resize:** Textarea grows with content (max-height: 600px)

---

### 3. Audio Player Component

**Purpose:** Custom audio controls with waveform visualization

#### Controls Layout

```
┌───────────────────────────────────────────────┐
│ [▶/⏸]  ━━━━━━━━━━━━━━━━━━━━━━●━━━  [⚙]     │
│ Play    0:32 / 2:45              Speed       │
│         [0.75x] [1.0x] [1.25x] [1.5x]       │
└───────────────────────────────────────────────┘
```

#### Visual Specifications

```css
/* Container */
height: 64px;
padding: var(--space-4);
background: var(--color-surface-elevated);
border-radius: var(--radius-lg);
box-shadow: var(--shadow-md);
display: flex;
align-items: center;
gap: var(--space-4);

/* Play button */
width: 40px;
height: 40px;
border-radius: var(--radius-full);
background: var(--color-interactive);
color: white;

/* Progress bar */
height: 4px;
background: var(--color-border-primary);
border-radius: var(--radius-full);

/* Progress fill */
background: var(--color-interactive);
transition: width 150ms ease-out;
```

#### Playback Speed Options

- **Values:** 0.75x, 1.0x, 1.25x, 1.5x, 2.0x
- **Active State:** Blue background, white text
- **Keyboard:** Number keys (1-5) to select speed

#### Waveform Visualization

- **Type:** Simple amplitude bars (optional enhancement)
- **Color:** `var(--color-audio-waveform)`
- **Interaction:** Click to seek

#### Accessibility

- **ARIA:** `role="region"` `aria-label="Audio player controls"`
- **Keyboard:**
  - Space: Play/Pause
  - J: Rewind 10s
  - L: Forward 10s
  - Arrow keys: Fine seek
- **Screen Reader:** Live region announces playback state changes
- **Touch Targets:** All buttons minimum 44x44px

---

### 4. Language Selector Component

**Purpose:** Dropdown for source/target language selection

#### Visual Design

```css
/* Select container */
min-height: 44px;
padding: var(--space-3) var(--space-4);
border: 1px solid var(--color-border-primary);
border-radius: var(--radius-md);
background: var(--color-surface-primary);
font-size: var(--font-size-base);

/* Hover */
border-color: var(--color-border-secondary);

/* Focus */
border-color: var(--color-interactive);
box-shadow: var(--shadow-focus);
```

#### Common Languages

Prioritize frequently used languages at top of dropdown:

1. English
2. Spanish
3. French
4. German
5. Hebrew
6. Russian
7. Chinese (Simplified)
8. Japanese
9. Arabic
10. Portuguese

Full list alphabetically after top 10.

#### Accessibility

- **ARIA:** `aria-label="Select source language"` / `"Select target language"`
- **Keyboard:** Arrow keys to navigate, Enter to select
- **Screen Reader:** Announces selected language on change

---

### 5. Button Component Variants

#### Primary Button

**Usage:** Main actions (Upload, Translate, Generate)

```css
background: var(--color-interactive);
color: var(--theme-text-inverse);
min-height: 44px;
padding: 12px 24px;
border-radius: var(--radius-md);
font-weight: 500;

/* Hover */
background: var(--color-interactive-hover);
transform: translateY(-1px);
box-shadow: var(--shadow-md);
```

#### Secondary Button

**Usage:** Alternative actions (Cancel, Edit, Back)

```css
background: transparent;
color: var(--color-text-primary);
border: 1px solid var(--color-border-primary);

/* Hover */
background: var(--color-surface-tertiary);
```

#### Danger Button

**Usage:** Destructive actions (Delete, Clear)

```css
background: var(--color-error);
color: white;

/* Hover */
background: #dc2626; /* Darker red */
```

#### Icon Button

**Usage:** Toolbar actions (Download, Share, Settings)

```css
width: 44px;
height: 44px;
padding: var(--space-3);
aspect-ratio: 1;
```

---

### 6. Progress Indicators

#### Linear Progress Bar

**Usage:** File upload progress

```css
height: 4px;
background: var(--color-border-primary);
border-radius: var(--radius-full);

/* Fill */
background: var(--color-interactive);
transition: width 200ms ease-out;
```

#### Indeterminate Progress

**Usage:** API processing (transcription, translation)

```css
.progress-bar--indeterminate .progress-bar__fill {
  width: 40%;
  animation: progress-indeterminate 1.5s infinite ease-in-out;
}

@keyframes progress-indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(250%); }
}
```

#### Circular Spinner

**Usage:** Button loading states

```css
width: 40px;
height: 40px;
border: 4px solid var(--color-border-primary);
border-top-color: var(--color-interactive);
border-radius: var(--radius-full);
animation: spin 0.8s linear infinite;
```

---

## Responsive Design

### Breakpoints (Mobile-First)

| Breakpoint | Width | Target Devices |
|------------|-------|----------------|
| `sm` | 640px | Tablets (portrait) |
| `md` | 768px | Tablets (landscape) |
| `lg` | 1024px | Laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large displays |

### Responsive Patterns

#### Stack on Mobile, Side-by-Side on Desktop

```css
/* Mobile: Stack vertically */
.responsive-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Desktop: Two columns */
@media (min-width: 768px) {
  .responsive-grid {
    flex-direction: row;
    gap: var(--space-6);
  }
}
```

#### Typography Scaling

```css
/* Mobile */
.hero-title {
  font-size: var(--font-size-2xl); /* 31px */
}

/* Desktop */
@media (min-width: 1024px) {
  .hero-title {
    font-size: var(--font-size-4xl); /* 49px */
  }
}
```

#### Touch Targets

**Mobile:** Minimum 44x44px (WCAG 2.1 AA)
**Desktop:** Can be smaller (cursor precision), but maintain 44px for consistency

---

## Animation Guidelines

### Transition Durations

| Speed | Duration | Usage |
|-------|----------|-------|
| Instant | 0ms | Reduced motion preference |
| Fast | 150ms | Hover states, color changes |
| Normal | 200ms | **Default for most interactions** |
| Slow | 300ms | Large element movements |
| Slower | 500ms | Page transitions |

### Easing Functions

```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);         /* Accelerate */
--ease-out: cubic-bezier(0, 0, 0.2, 1);        /* Decelerate (default) */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);   /* Smooth both ends */
--ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Bounce */
```

**Guidelines:**
- Use `ease-out` for entering elements (fast start, slow end)
- Use `ease-in` for exiting elements (slow start, fast end)
- Use `ease-spring` sparingly for playful micro-interactions

### Respect Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

All animations automatically disable for users who prefer reduced motion.

---

## Accessibility

### WCAG 2.1 Compliance

**Target Level:** AA minimum, AAA where possible

#### Color Contrast

| Element | Light Theme | Dark Theme | Level |
|---------|-------------|------------|-------|
| Primary text | 15.8:1 | 14.5:1 | AAA |
| Secondary text | 8.6:1 | 9.3:1 | AAA |
| Tertiary text | 4.6:1 | 4.7:1 | AA |
| Interactive elements | 4.5:1 | 7.6:1 | AA/AAA |

#### Touch Targets

- **Minimum:** 44x44px (WCAG 2.1 Level AA)
- **Comfortable:** 48x48px
- **Large:** 56x56px (primary actions)

#### Keyboard Navigation

All interactive elements support:
- **Tab:** Move to next element
- **Shift+Tab:** Move to previous element
- **Enter/Space:** Activate button/link
- **Escape:** Close modal/dropdown
- **Arrow keys:** Navigate within component

#### Screen Reader Support

**ARIA Attributes:**
- `role`: Define element purpose
- `aria-label`: Provide descriptive label
- `aria-describedby`: Link to help text
- `aria-live`: Announce dynamic updates
- `aria-pressed`: Toggle button state

**Example:**
```html
<button
  class="btn-primary"
  aria-label="Upload audio file"
  aria-describedby="upload-help"
>
  Upload
</button>
<span id="upload-help" class="sr-only">
  Maximum file size: 25 MB. Supported formats: MP3, WAV, OGG, M4A
</span>
```

#### Focus Management

- **Visible Focus Rings:** Always visible in both themes
- **Focus Trap:** Modals trap focus until closed
- **Focus Restoration:** Return focus after modal closes
- **Skip Links:** "Skip to main content" for screen readers

---

## Component State Matrix

| Component | Default | Hover | Focus | Active | Disabled | Loading | Success | Error |
|-----------|---------|-------|-------|--------|----------|---------|---------|-------|
| Button | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | - | - |
| Upload Zone | ✓ | ✓ | ✓ | ✓ (dragging) | - | ✓ | ✓ | ✓ |
| Transcript | ✓ | - | ✓ | ✓ (editing) | ✓ (readonly) | ✓ | - | ✓ |
| Audio Player | ✓ | ✓ | ✓ | ✓ (playing) | ✓ | ✓ | - | ✓ |
| Form Input | ✓ | ✓ | ✓ | - | ✓ | - | ✓ | ✓ |
| Language Select | ✓ | ✓ | ✓ | ✓ (open) | ✓ | - | - | ✓ |

**All states must:**
- Have clear visual differentiation
- Announce state to screen readers
- Respect `prefers-reduced-motion`

---

## Design Tokens Summary

### Quick Reference

**Colors:**
- Interactive: `var(--color-interactive)`
- Text: `var(--color-text-primary)`
- Background: `var(--color-surface-primary)`
- Border: `var(--color-border-primary)`

**Spacing:**
- Small gap: `var(--space-2)` (8px)
- Standard: `var(--space-4)` (16px)
- Section: `var(--space-6)` (24px)

**Typography:**
- Body: `var(--font-size-base)` (16px)
- Heading: `var(--font-size-xl)` (25px)
- Small: `var(--font-size-sm)` (13px)

**Timing:**
- Fast: `var(--duration-fast)` (150ms)
- Normal: `var(--duration-normal)` (200ms)

---

## Version History

### v1.0 (2025-12-09)
- Initial design system
- Dark/Light theme support
- Complete component specifications
- Accessibility guidelines (WCAG 2.1 AA)
- Responsive breakpoints
- Animation guidelines

---

## Resources

**Design Files:**
- `/design/design-tokens.css` - CSS custom properties
- `/design/component-styles.css` - Component classes
- `/design/UI_FLOW_SPEC.md` - User journey wireframes
- `/design/ACCESSIBILITY_CHECKLIST.md` - A11y requirements

**External References:**
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN: CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [Inclusive Components](https://inclusive-components.design/)

---

**Questions or Feedback?**
See `/design/DESIGN_HANDOFF.md` for integration instructions.
