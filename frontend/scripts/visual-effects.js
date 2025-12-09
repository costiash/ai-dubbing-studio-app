/**
 * PHASE 4: VISUAL EFFECTS - Interactive Animations
 *
 * "Sonic Laboratory" Kinetic Interactions:
 * - Ripple effects on clicks
 * - Particle system during processing
 * - Waveform visualizations
 * - Smooth page transitions
 * - Custom cursor
 */

/**
 * Ripple Effect on Button Clicks
 * Creates expanding circular ripple from click point
 */
export class RippleEffect {
  constructor() {
    this.setupRipples();
  }

  setupRipples() {
    // Add ripple to all buttons
    document.addEventListener('click', (e) => {
      const button = e.target.closest('.btn');
      if (!button) return;

      const ripple = document.createElement('span');
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;

      ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        top: ${y}px;
        left: ${x}px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple-expand 0.6s ease-out;
        pointer-events: none;
        z-index: 1;
      `;

      button.style.position = 'relative';
      button.style.overflow = 'hidden';
      button.appendChild(ripple);

      ripple.addEventListener('animationend', () => {
        ripple.remove();
      });
    });

    // Add ripple animation to stylesheet
    if (!document.querySelector('#ripple-animation')) {
      const style = document.createElement('style');
      style.id = 'ripple-animation';
      style.textContent = `
        @keyframes ripple-expand {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }
}

/**
 * Particle System
 * Floating particles during audio processing
 */
export class ParticleSystem {
  constructor() {
    this.particles = [];
    this.container = null;
    this.animationFrame = null;
    this.isRunning = false;
  }

  start() {
    if (this.isRunning) return;

    this.isRunning = true;

    // Create container
    this.container = document.createElement('div');
    this.container.className = 'particle-container';
    this.container.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 9998;
      overflow: hidden;
    `;
    document.body.appendChild(this.container);

    // Create particles
    for (let i = 0; i < 30; i++) {
      setTimeout(() => this.createParticle(), i * 100);
    }

    this.animate();
  }

  stop() {
    this.isRunning = false;

    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }

    if (this.container) {
      this.container.style.opacity = '0';
      setTimeout(() => {
        this.container?.remove();
        this.container = null;
      }, 500);
    }

    this.particles = [];
  }

  createParticle() {
    if (!this.container) return;

    const particle = document.createElement('div');
    const size = Math.random() * 4 + 2;
    const x = Math.random() * window.innerWidth;
    const y = window.innerHeight + 20;
    const hue = Math.random() * 60 + 170; // Cyan to blue range

    particle.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: hsl(${hue}, 100%, 70%);
      border-radius: 50%;
      box-shadow: 0 0 ${size * 3}px hsl(${hue}, 100%, 70%);
      opacity: 0.8;
      transition: opacity 0.5s;
    `;

    this.container.appendChild(particle);

    this.particles.push({
      element: particle,
      x: x,
      y: y,
      vx: (Math.random() - 0.5) * 2,
      vy: -(Math.random() * 2 + 1),
      life: 1.0,
    });
  }

  animate() {
    if (!this.isRunning) return;

    this.particles = this.particles.filter(particle => {
      particle.y += particle.vy;
      particle.x += particle.vx;
      particle.life -= 0.005;

      if (particle.life <= 0 || particle.y < -20) {
        particle.element.remove();
        return false;
      }

      particle.element.style.left = `${particle.x}px`;
      particle.element.style.top = `${particle.y}px`;
      particle.element.style.opacity = particle.life * 0.8;

      return true;
    });

    // Create new particles occasionally
    if (this.particles.length < 30 && Math.random() < 0.05) {
      this.createParticle();
    }

    this.animationFrame = requestAnimationFrame(() => this.animate());
  }
}

/**
 * Waveform Visualization
 * Animated audio waveform during transcription
 */
export class WaveformVisualizer {
  constructor(container) {
    this.container = container;
    this.canvas = null;
    this.ctx = null;
    this.animationFrame = null;
    this.isPlaying = false;
    this.bars = 32;
    this.barHeights = new Array(this.bars).fill(0.1);
  }

  init() {
    // Create canvas
    this.canvas = document.createElement('canvas');
    this.canvas.style.cssText = `
      width: 100%;
      height: 80px;
      display: block;
    `;
    this.container.appendChild(this.canvas);

    // Set actual canvas size (for retina)
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;

    this.ctx = this.canvas.getContext('2d');
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  start() {
    if (this.isPlaying) return;
    if (!this.canvas) this.init();

    this.isPlaying = true;
    this.animate();
  }

  stop() {
    this.isPlaying = false;
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }

  animate() {
    if (!this.isPlaying || !this.ctx) return;

    const width = this.canvas.width / window.devicePixelRatio;
    const height = this.canvas.height / window.devicePixelRatio;
    const barWidth = width / this.bars;

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Update bar heights with random movement
    this.barHeights = this.barHeights.map((h, i) => {
      const target = Math.random() * 0.8 + 0.2;
      return h + (target - h) * 0.1;
    });

    // Draw bars
    this.barHeights.forEach((h, i) => {
      const x = i * barWidth;
      const barHeight = h * height * 0.8;
      const y = (height - barHeight) / 2;

      // Gradient from cyan to coral
      const gradient = this.ctx.createLinearGradient(0, y, 0, y + barHeight);
      gradient.addColorStop(0, '#00fff5');
      gradient.addColorStop(1, '#ff8e53');

      this.ctx.fillStyle = gradient;
      this.ctx.fillRect(x + 2, y, barWidth - 4, barHeight);

      // Glow effect
      this.ctx.shadowBlur = 10;
      this.ctx.shadowColor = '#00fff5';
    });

    this.animationFrame = requestAnimationFrame(() => this.animate());
  }

  destroy() {
    this.stop();
    if (this.canvas) {
      this.canvas.remove();
      this.canvas = null;
    }
  }
}

/**
 * Custom Cursor
 * Audio-themed cursor for the entire app
 */
export class CustomCursor {
  constructor() {
    this.cursor = null;
    this.cursorDot = null;
    this.mouseX = 0;
    this.mouseY = 0;
    this.dotX = 0;
    this.dotY = 0;
    this.boundHandlers = {}; // Store bound event listeners for cleanup
    this.animationFrameId = null; // Store RAF ID for cleanup
  }

  init() {
    // Create cursor elements
    this.cursor = document.createElement('div');
    this.cursor.className = 'custom-cursor';
    this.cursor.style.cssText = `
      position: fixed;
      width: 32px;
      height: 32px;
      border: 2px solid var(--sonic-accent-cyan);
      border-radius: 50%;
      pointer-events: none;
      z-index: 10001;
      transition: all 0.2s ease;
      opacity: 0;
      transform: translate(-50%, -50%);
    `;

    this.cursorDot = document.createElement('div');
    this.cursorDot.className = 'custom-cursor-dot';
    this.cursorDot.style.cssText = `
      position: fixed;
      width: 6px;
      height: 6px;
      background: var(--sonic-accent-cyan);
      border-radius: 50%;
      pointer-events: none;
      z-index: 10002;
      opacity: 0;
      transform: translate(-50%, -50%);
      box-shadow: 0 0 10px var(--sonic-glow-cyan);
    `;

    document.body.appendChild(this.cursor);
    document.body.appendChild(this.cursorDot);

    // Track mouse movement - store bound handler
    this.boundHandlers.mousemove = (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;

      this.cursor.style.left = `${e.clientX}px`;
      this.cursor.style.top = `${e.clientY}px`;
      this.cursor.style.opacity = '1';
      this.cursorDot.style.opacity = '1';

      // Smooth follow for dot
      this.animateDot();
    };
    document.addEventListener('mousemove', this.boundHandlers.mousemove);

    // Hide cursor when leaving window - store bound handler
    this.boundHandlers.mouseleave = () => {
      this.cursor.style.opacity = '0';
      this.cursorDot.style.opacity = '0';
    };
    document.addEventListener('mouseleave', this.boundHandlers.mouseleave);

    // Scale up on click - store bound handler
    this.boundHandlers.mousedown = () => {
      this.cursor.style.transform = 'translate(-50%, -50%) scale(0.8)';
    };
    document.addEventListener('mousedown', this.boundHandlers.mousedown);

    this.boundHandlers.mouseup = () => {
      this.cursor.style.transform = 'translate(-50%, -50%) scale(1)';
    };
    document.addEventListener('mouseup', this.boundHandlers.mouseup);

    // Change cursor on hover over interactive elements - store bound handler
    this.boundHandlers.mouseover = (e) => {
      if (e.target.closest('button, a, input, textarea, select, [role="button"]')) {
        this.cursor.style.width = '48px';
        this.cursor.style.height = '48px';
        this.cursor.style.borderColor = 'var(--sonic-accent-coral)';
      } else {
        this.cursor.style.width = '32px';
        this.cursor.style.height = '32px';
        this.cursor.style.borderColor = 'var(--sonic-accent-cyan)';
      }
    };
    document.addEventListener('mouseover', this.boundHandlers.mouseover);

    // Hide default cursor
    document.body.style.cursor = 'none';
    document.querySelectorAll('a, button, input, textarea, select').forEach(el => {
      el.style.cursor = 'none';
    });
  }

  animateDot() {
    this.dotX += (this.mouseX - this.dotX) * 0.2;
    this.dotY += (this.mouseY - this.dotY) * 0.2;

    this.cursorDot.style.left = `${this.dotX}px`;
    this.cursorDot.style.top = `${this.dotY}px`;

    // Store RAF ID for cleanup
    this.animationFrameId = requestAnimationFrame(() => this.animateDot());
  }

  destroy() {
    // Cancel animation frame
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    // Remove all event listeners using stored bound handlers
    if (this.boundHandlers.mousemove) {
      document.removeEventListener('mousemove', this.boundHandlers.mousemove);
    }
    if (this.boundHandlers.mouseleave) {
      document.removeEventListener('mouseleave', this.boundHandlers.mouseleave);
    }
    if (this.boundHandlers.mousedown) {
      document.removeEventListener('mousedown', this.boundHandlers.mousedown);
    }
    if (this.boundHandlers.mouseup) {
      document.removeEventListener('mouseup', this.boundHandlers.mouseup);
    }
    if (this.boundHandlers.mouseover) {
      document.removeEventListener('mouseover', this.boundHandlers.mouseover);
    }

    // Clear bound handlers
    this.boundHandlers = {};

    // Remove cursor elements
    if (this.cursor) {
      this.cursor.remove();
      this.cursor = null;
    }
    if (this.cursorDot) {
      this.cursorDot.remove();
      this.cursorDot = null;
    }

    // Restore default cursor on body
    document.body.style.cursor = 'auto';

    // Restore inline cursor styles on all interactive elements
    document.querySelectorAll('a, button, input, textarea, select').forEach(el => {
      el.style.cursor = '';
    });
  }
}

/**
 * Smooth Page Transitions
 * Fade between sections with scale effect
 */
export class PageTransitions {
  constructor() {
    this.setupObserver();
  }

  setupObserver() {
    // Observe section visibility changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
          const target = mutation.target;
          if (target.classList.contains('section')) {
            this.animateSection(target);
          }
        }
      });
    });

    document.querySelectorAll('.section').forEach((section) => {
      observer.observe(section, { attributes: true });
    });
  }

  animateSection(section) {
    if (!section.classList.contains('hidden')) {
      section.style.animation = 'fadeInScale 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    }
  }
}

/**
 * Audio Reactive UI
 * Make UI elements pulse during audio playback
 */
export class AudioReactiveUI {
  constructor() {
    this.isReacting = false;
    this.analyser = null;
  }

  start(audioElement) {
    if (this.isReacting) return;

    this.isReacting = true;

    // Simple visual feedback without Web Audio API
    // Pulse border colors when audio is playing
    audioElement.addEventListener('play', () => {
      document.querySelectorAll('.audio-player').forEach(player => {
        player.style.animation = 'audio-pulse 1s ease-in-out infinite';
      });
    });

    audioElement.addEventListener('pause', () => {
      document.querySelectorAll('.audio-player').forEach(player => {
        player.style.animation = 'none';
      });
    });

    // Add pulse animation
    if (!document.querySelector('#audio-pulse-animation')) {
      const style = document.createElement('style');
      style.id = 'audio-pulse-animation';
      style.textContent = `
        @keyframes audio-pulse {
          0%, 100% {
            border-color: var(--sonic-border);
            box-shadow: 0 0 0 rgba(0, 217, 255, 0);
          }
          50% {
            border-color: var(--sonic-accent-cyan);
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  stop() {
    this.isReacting = false;
    document.querySelectorAll('.audio-player').forEach(player => {
      player.style.animation = 'none';
    });
  }
}

/**
 * Initialize all visual effects
 * Called from main.js when app loads
 */
export function initVisualEffects() {
  // Check if user prefers reduced motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (prefersReducedMotion) {
    console.log('Reduced motion preference detected - skipping advanced animations');
    return;
  }

  // Initialize effects
  const rippleEffect = new RippleEffect();
  const pageTransitions = new PageTransitions();

  // Custom cursor (optional - can be disabled on mobile)
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  let customCursor = null;
  if (!isMobile) {
    customCursor = new CustomCursor();
    customCursor.init();
  }

  // Return controllers for other modules to use
  return {
    particles: new ParticleSystem(),
    waveform: new WaveformVisualizer(document.querySelector('#waveform-container')),
    audioReactive: new AudioReactiveUI(),
    customCursor: customCursor, // Return customCursor instance for cleanup
  };
}
