---
paths: frontend/**/*.js
---

# Frontend JavaScript Rules

## Code Style

- ES6 modules: Use `import`/`export`, not CommonJS
- Dependency injection: Pass dependencies in constructors
- No global state: Don't use `window.` for app state

## Architecture

Manager pattern in `frontend/scripts/managers/`:
- `UIStateManager` - Section visibility, display state
- `UIFeedbackManager` - Loading overlays, error toasts
- `FileUploadManager` - Upload workflow
- `AudioProcessingManager` - Translation/TTS workflow

## Race Condition Prevention

```javascript
import { lockUI, unlockUI } from './utils/ui-lock.js';

async handleOperation() {
  if (this.isProcessing) return;  // Guard flag
  this.isProcessing = true;
  try {
    lockUI('processing');
    await this.apiClient.operation();
  } catch (error) {
    this.uiFeedbackManager.showError(error.message);
  } finally {
    this.isProcessing = false;
    unlockUI();
  }
}
```

## Security

- XSS prevention: Use `element.textContent`, NEVER `innerHTML` with user data
- API errors: Display message, don't expose stack traces

## Session Persistence

```javascript
import sessionManager from './session.js';

sessionManager.saveState('transcription', text);  // After each step
sessionManager.getState('transcription');         // On page load
sessionManager.clearState();                      // On reset
```

## Testing

- Framework: Vitest with jsdom
- Mock all API calls and visual effects
- Test files in `frontend/tests/` mirror source structure

```bash
cd frontend && npm test           # Run tests
cd frontend && npm run test:ui    # Interactive UI
cd frontend && npm run test:coverage
```
