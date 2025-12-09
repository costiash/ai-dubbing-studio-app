import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: [
        'scripts/managers/**/*.js',
        'scripts/services/**/*.js',
        'scripts/utils/**/*.js'
      ],
      exclude: [
        'node_modules/',
        'tests/',
      ],
      thresholds: {
        lines: 75,
        functions: 75,
        branches: 70,
        statements: 75
      }
    },
  },
});
