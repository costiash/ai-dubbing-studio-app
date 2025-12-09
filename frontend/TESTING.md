# Frontend Testing Documentation

Comprehensive test suite for the AI Dubbing Studio frontend using **Vitest + jsdom**.

## Test Coverage

**Current Coverage: 100% statements, 90.43% branches, 100% functions, 100% lines**

Coverage is measured on the refactored modules:
- `scripts/managers/` - Business logic managers
- `scripts/services/` - Service layer (health checks)
- `scripts/utils/` - Utility functions (UI locking)

### Coverage by Module

| Module | Statements | Branches | Functions | Lines |
|--------|-----------|----------|-----------|-------|
| **managers/** | 100% | 86.9% | 100% | 100% |
| AudioProcessingManager.js | 100% | 90.9% | 100% | 100% |
| FileUploadManager.js | 100% | 75% | 100% | 100% |
| UIFeedbackManager.js | 100% | 100% | 100% | 100% |
| UIStateManager.js | 100% | 84.37% | 100% | 100% |
| **services/** | 100% | 100% | 100% | 100% |
| HealthCheckService.js | 100% | 100% | 100% | 100% |
| **utils/** | 100% | 100% | 100% | 100% |
| ui-lock.js | 100% | 100% | 100% | 100% |

## Quick Start

### Install Dependencies

```bash
cd /home/rudycosta3/ai-dubbing-studio-app/frontend
npm install
```

### Run Tests

```bash
# Run all tests once
npm test

# Watch mode (re-run on file changes)
npm run test:watch

# Interactive UI mode
npm run test:ui

# Generate coverage report
npm run test:coverage
```

## Test Structure

```
frontend/
├── tests/
│   ├── setup.js                           # Global test setup
│   ├── utils/
│   │   └── ui-lock.test.js               # UI locking utility tests (19 tests)
│   ├── managers/
│   │   ├── FileUploadManager.test.js     # Upload workflow tests (21 tests)
│   │   ├── AudioProcessingManager.test.js # Translation/TTS tests (33 tests)
│   │   ├── UIStateManager.test.js        # UI state management tests (37 tests)
│   │   └── UIFeedbackManager.test.js     # User feedback tests (39 tests)
│   ├── services/
│   │   └── HealthCheckService.test.js    # Backend health check tests (14 tests)
│   └── integration/
│       └── app-workflow.test.js          # End-to-end workflow tests (14 tests)
└── vitest.config.js                       # Vitest configuration
```

**Total: 163 tests across 7 test files**

## What's Tested

### Unit Tests

#### ui-lock.js (19 tests)
- ✅ Lock/unlock all interactive elements (buttons, inputs, selects)
- ✅ ARIA attributes for accessibility (aria-busy, aria-disabled, aria-label)
- ✅ Tabindex management for keyboard navigation
- ✅ Graceful handling of missing DOM elements
- ✅ Multiple lock/unlock cycles

#### FileUploadManager.js (21 tests)
- ✅ File upload and transcription workflow
- ✅ Race condition prevention (isUploading guard)
- ✅ UI locking during upload
- ✅ WaveformVisualizer integration
- ✅ State updates and session persistence
- ✅ Error handling and UI unlocking
- ✅ Optional dependency handling (WaveformVisualizer)

#### AudioProcessingManager.js (33 tests)
- ✅ Translation and TTS generation workflow
- ✅ Race condition prevention (isProcessing guard)
- ✅ Input validation (text length, required fields)
- ✅ UI locking during processing
- ✅ ParticleSystem integration
- ✅ API error handling (translation, TTS)
- ✅ Download functionality
- ✅ Helper methods (capitalize)
- ✅ Optional dependency handling (ParticleSystem)

#### UIStateManager.js (37 tests)
- ✅ Section visibility management (upload, transcribe, results)
- ✅ Character count updates with thresholds
- ✅ Audio player loading
- ✅ AudioReactiveUI event wiring
- ✅ Transcript/translation display
- ✅ Reset functionality
- ✅ Language capitalization

#### UIFeedbackManager.js (39 tests)
- ✅ Loading overlay show/hide
- ✅ Loading message updates
- ✅ Upload progress indicator
- ✅ Error toast display with auto-dismiss
- ✅ Multiple error handling
- ✅ Graceful handling of missing DOM elements
- ✅ Workflow integration tests

#### HealthCheckService.js (14 tests)
- ✅ Backend API health checks
- ✅ OpenAI API configuration validation
- ✅ Connection error handling
- ✅ User-friendly error messages
- ✅ Console logging

### Integration Tests

#### app-workflow.test.js (14 tests)
- ✅ Upload → Transcribe flow
- ✅ Translate → TTS flow
- ✅ Full end-to-end: Upload → Transcribe → Translate → TTS → Download
- ✅ Race condition prevention across workflows
- ✅ Error handling at each step
- ✅ Error recovery and retry
- ✅ Reset workflow
- ✅ State management across steps

## Testing Best Practices

### Mocking Strategy

All external dependencies are mocked:
- **API Client** - Mock fetch calls and responses
- **Visual Effects** - Mock WaveformVisualizer, ParticleSystem, AudioReactiveUI
- **DOM Storage** - Mock localStorage and sessionStorage
- **URL APIs** - Mock URL.createObjectURL

Example:
```javascript
vi.mock('../../scripts/utils/ui-lock.js', () => ({
  lockUI: vi.fn(),
  unlockUI: vi.fn()
}));
```

### DOM Setup

Each test sets up required DOM elements in `beforeEach`:
```javascript
beforeEach(() => {
  document.body.innerHTML = `
    <button id="translate-btn"></button>
    <textarea id="transcript-editor"></textarea>
    <!-- ... more elements -->
  `;
});
```

### Async Testing

All async operations are properly awaited:
```javascript
it('should upload file successfully', async () => {
  await manager.handleFileUpload(mockFile);
  expect(mockState.transcription).toBe('Expected text');
});
```

### Error Path Testing

Tests cover both happy paths and error scenarios:
```javascript
it('should handle API errors gracefully', async () => {
  mockApiClient.transcribeAudio.mockRejectedValue(new Error('Network error'));
  await manager.handleFileUpload(mockFile);
  expect(mockUIFeedbackManager.showError).toHaveBeenCalled();
  expect(uiLock.unlockUI).toHaveBeenCalled(); // Ensures cleanup
});
```

## Configuration

### vitest.config.js

```javascript
export default defineConfig({
  test: {
    environment: 'jsdom',           // Browser-like environment
    globals: true,                  // Global test functions
    setupFiles: ['./tests/setup.js'], // Global setup
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: [
        'scripts/managers/**/*.js',
        'scripts/services/**/*.js',
        'scripts/utils/**/*.js'
      ],
      thresholds: {
        lines: 75,
        functions: 75,
        branches: 70,
        statements: 75
      }
    }
  }
});
```

### Coverage Thresholds

- **Lines:** 75% (Currently 100%)
- **Functions:** 75% (Currently 100%)
- **Branches:** 70% (Currently 90.43%)
- **Statements:** 75% (Currently 100%)

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Frontend Tests
  run: |
    cd frontend
    npm install
    npm test

- name: Check Coverage
  run: |
    cd frontend
    npm run test:coverage
```

## Troubleshooting

### Tests Fail with "Cannot find module"

Ensure `"type": "module"` is set in `package.json`:
```json
{
  "type": "module"
}
```

### Coverage Report Not Generated

Install coverage provider:
```bash
npm install --save-dev @vitest/coverage-v8
```

### JSDOM Errors

Ensure `jsdom` is installed and environment is set:
```bash
npm install --save-dev jsdom
```

### Mock Not Working

Clear mocks between tests:
```javascript
beforeEach(() => {
  vi.clearAllMocks();
});
```

## Future Enhancements

Potential areas for additional testing:
- [ ] Legacy modules (api.js, audio.js, main.js, upload.js, theme.js, session.js, visual-effects.js)
- [ ] Visual regression testing
- [ ] E2E testing with Playwright
- [ ] Performance testing
- [ ] Accessibility testing (automated a11y checks)

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [JSDOM Documentation](https://github.com/jsdom/jsdom)
- [JavaScript Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)

---

**Last Updated:** 2025-12-10
**Test Count:** 163 tests
**Coverage:** 100% statements, 90.43% branches, 100% functions, 100% lines
