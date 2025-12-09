# Testing Checklist - AI Dubbing Studio

Complete testing checklist for validating the frontend and backend integration.

## Pre-Testing Setup

- [ ] Backend running at `http://localhost:8000`
- [ ] Frontend running at `http://localhost:3000`
- [ ] OpenAI API key configured in `.env`
- [ ] FFmpeg installed and in PATH
- [ ] Test audio files prepared (MP3, WAV, OGG, M4A)

### Test Audio Files

Create or download small test files:
- `test.mp3` (1-2 MB, 10-30 seconds)
- `test.wav` (< 25 MB)
- `test.ogg` (1-2 MB)
- `test.m4a` (1-2 MB)

## Functional Testing

### 1. Backend API Health Check

**Test**: Verify backend is running
```bash
curl http://localhost:8000/health
```

**Expected Result**:
```json
{
  "status": "healthy",
  "openai_api_configured": true,
  "version": "v1"
}
```

**Status**: [ ]

---

### 2. File Upload - Drag and Drop

**Test Steps**:
1. Open `http://localhost:3000`
2. Drag `test.mp3` onto the upload zone
3. Observe visual feedback (zone highlights)
4. Drop file

**Expected Result**:
- Upload zone highlights on dragover
- Progress indicator appears
- Backend processes file
- Transcription section appears

**Status**: [ ]

---

### 3. File Upload - Click to Browse

**Test Steps**:
1. Refresh page
2. Click upload zone
3. Select `test.mp3` from file picker
4. Click "Open"

**Expected Result**:
- File picker opens
- Selected file uploads
- Transcription appears

**Status**: [ ]

---

### 4. File Upload - Invalid File Type

**Test Steps**:
1. Try uploading a `.txt` or `.jpg` file

**Expected Result**:
- Error toast appears: "Invalid file type. Please upload an audio file: .mp3, .wav, .ogg, .m4a"
- No API call made

**Status**: [ ]

---

### 5. File Upload - File Too Large

**Test Steps**:
1. Try uploading a file > 25 MB

**Expected Result**:
- Error toast: "File too large. Maximum size is 25 MB. Your file is X MB."
- No API call made

**Status**: [ ]

---

### 6. Transcription

**Test Steps**:
1. Upload valid audio file (Hebrew speech)
2. Wait for transcription

**Expected Result**:
- Progress indicator shows
- Transcription appears in textarea
- Source language detected correctly (Hebrew)
- Character count updates
- Original audio player loads

**Status**: [ ]

---

### 7. Transcript Editing

**Test Steps**:
1. After transcription appears
2. Click in transcript textarea
3. Edit text (add/remove characters)
4. Observe character count

**Expected Result**:
- Textarea is editable
- Character count updates in real-time
- Count shows "X / 50,000"
- Warning color at 90% (45,000 chars)
- Error color at 100% (50,000 chars)

**Status**: [ ]

---

### 8. Language Selection

**Test Steps**:
1. After transcription
2. Change source language dropdown
3. Change target language dropdown

**Expected Result**:
- Dropdown values change
- No API calls triggered yet
- UI remains responsive

**Status**: [ ]

---

### 9. Voice Selection

**Test Steps**:
1. Select different voices from dropdown
   - Alloy
   - Echo
   - Fable
   - Onyx (default)
   - Nova
   - Shimmer

**Expected Result**:
- Dropdown selection changes
- No API calls until "Translate & Generate" clicked

**Status**: [ ]

---

### 10. TTS Model Selection

**Test Steps**:
1. Select "Standard (Faster)"
2. Select "High Definition (Slower)"

**Expected Result**:
- Model selection changes
- No API calls until button clicked

**Status**: [ ]

---

### 11. Audio Player - Original Audio

**Test Steps**:
1. After transcription
2. Click play button on original audio player
3. Click pause
4. Click progress bar to seek
5. Try playback speed buttons (0.75x, 1.0x, 1.25x, 1.5x)

**Expected Result**:
- Audio plays
- Play icon changes to pause icon
- Progress bar animates
- Seek works correctly
- Time displays update (MM:SS format)
- Playback speed changes

**Status**: [ ]

---

### 12. Audio Player - Keyboard Shortcuts

**Test Steps**:
1. With audio player visible
2. Press `Space` to play/pause
3. Press `J` to skip backward 10 seconds
4. Press `L` to skip forward 10 seconds
5. Press `←` (left arrow) to skip backward
6. Press `→` (right arrow) to skip forward

**Expected Result**:
- Space toggles play/pause
- J and ← skip backward
- L and → skip forward
- Shortcuts don't interfere with text inputs

**Status**: [ ]

---

### 13. Translation & TTS Generation

**Test Steps**:
1. After transcription
2. Select source: Hebrew
3. Select target: Russian
4. Select voice: Onyx
5. Select model: Standard
6. Click "Translate & Generate Speech"

**Expected Result**:
- Loading overlay appears: "Translating text..."
- Then: "Generating speech..."
- Results section appears
- Two audio players visible (Original vs Generated)
- Transcripts displayed in both languages
- Success alert shown

**Status**: [ ]

---

### 14. Results - Audio Comparison

**Test Steps**:
1. After TTS generation
2. Play original audio
3. Play generated audio
4. Compare side-by-side

**Expected Result**:
- Both players work independently
- Can play both at same time (if desired)
- Generated audio is in target language
- Audio quality is acceptable

**Status**: [ ]

---

### 15. Download Generated Audio

**Test Steps**:
1. After TTS generation
2. Click "Download MP3" button

**Expected Result**:
- Browser download starts
- File name: `dubbed_audio_russian_<timestamp>.mp3`
- File is valid MP3 format
- File plays in media player

**Status**: [ ]

---

### 16. Start New Project

**Test Steps**:
1. After completing a project
2. Click "Start New" button

**Expected Result**:
- App resets to upload screen
- All state cleared
- Upload zone re-enabled
- Session cleared from localStorage
- Previous audio URLs revoked

**Status**: [ ]

---

### 17. Theme Toggle - Light to Dark

**Test Steps**:
1. Open app (default light theme)
2. Click sun/moon icon in top-right
3. Observe theme change

**Expected Result**:
- Theme smoothly transitions to dark mode
- All colors invert appropriately
- Icon changes from sun to moon
- Preference saved to localStorage
- ARIA label updates

**Status**: [ ]

---

### 18. Theme Toggle - Dark to Light

**Test Steps**:
1. With dark theme active
2. Click moon icon
3. Observe theme change

**Expected Result**:
- Theme transitions to light mode
- Colors revert to light theme
- Icon changes to sun
- Preference saved

**Status**: [ ]

---

### 19. Theme Toggle - Keyboard Navigation

**Test Steps**:
1. Press `Tab` repeatedly until theme toggle focused
2. Press `Enter` or `Space` to toggle

**Expected Result**:
- Focus indicator visible on toggle button
- Enter/Space toggles theme
- Keyboard navigation works smoothly

**Status**: [ ]

---

### 20. Session Persistence

**Test Steps**:
1. Upload and transcribe audio
2. Refresh browser (F5)
3. Check if session restored

**Expected Result**:
- Session is NOT automatically restored (by design)
- User must re-upload file
- Theme preference IS preserved

**Status**: [ ]

---

### 21. Error Handling - Backend Offline

**Test Steps**:
1. Stop backend server
2. Try uploading audio file

**Expected Result**:
- Error toast appears: "Cannot connect to backend server..."
- User can retry after restarting backend

**Status**: [ ]

---

### 22. Error Handling - Invalid API Response

**Test Steps**:
1. Upload invalid audio file (corrupted MP3)

**Expected Result**:
- Error toast shows backend error message
- User can try different file
- App doesn't crash

**Status**: [ ]

---

### 23. Error Handling - Network Timeout

**Test Steps**:
1. Upload very large file (close to 25 MB limit)
2. Simulate slow network (Chrome DevTools → Network → Slow 3G)

**Expected Result**:
- Loading indicator shows for extended time
- Eventually completes or times out gracefully
- Error message shown if timeout occurs

**Status**: [ ]

---

## Accessibility Testing

### 24. Keyboard Navigation - Full Workflow

**Test Steps**:
1. Open app
2. Use only keyboard (no mouse)
3. Tab through all elements
4. Complete upload → transcribe → translate → download

**Expected Result**:
- All interactive elements reachable via Tab
- Focus indicators visible
- Enter/Space activates buttons
- No keyboard traps

**Status**: [ ]

---

### 25. Screen Reader - NVDA/JAWS (Windows)

**Test Steps**:
1. Enable NVDA or JAWS
2. Navigate app with keyboard
3. Listen to announcements

**Expected Result**:
- All elements have descriptive labels
- ARIA roles announced correctly
- Status updates announced (aria-live regions)
- Forms properly labeled

**Status**: [ ]

---

### 26. Screen Reader - VoiceOver (Mac/iOS)

**Test Steps**:
1. Enable VoiceOver (Cmd+F5 on Mac)
2. Navigate with VO keys
3. Test on iPhone/iPad

**Expected Result**:
- Same as NVDA/JAWS
- Touch targets at least 44x44px on mobile
- Gestures work on iOS

**Status**: [ ]

---

### 27. Color Contrast - Light Theme

**Test Steps**:
1. Switch to light theme
2. Use axe DevTools or WAVE extension
3. Check for contrast issues

**Expected Result**:
- All text meets WCAG AA (4.5:1 minimum)
- Headings/large text meet AAA (7:1+)
- No contrast violations reported

**Status**: [ ]

---

### 28. Color Contrast - Dark Theme

**Test Steps**:
1. Switch to dark theme
2. Run axe DevTools
3. Check contrast

**Expected Result**:
- Same as light theme
- Dark theme text readable
- No contrast violations

**Status**: [ ]

---

### 29. Reduced Motion Preference

**Test Steps**:
1. Enable "Reduce motion" in OS settings
   - macOS: System Preferences → Accessibility → Display → Reduce motion
   - Windows: Settings → Ease of Access → Display → Show animations
2. Test animations in app

**Expected Result**:
- All transitions become instant (0ms)
- No animations play
- Functionality remains intact

**Status**: [ ]

---

## Responsive Design Testing

### 30. Mobile Phone (Portrait)

**Test Steps**:
1. Open Chrome DevTools
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select "iPhone 12" or similar
4. Test full workflow

**Expected Result**:
- Layout adapts to narrow screen
- Touch targets at least 44x44px
- Text readable without zooming
- No horizontal scrolling
- Upload zone usable

**Status**: [ ]

---

### 31. Mobile Phone (Landscape)

**Test Steps**:
1. Rotate device to landscape
2. Test interface

**Expected Result**:
- Layout adjusts appropriately
- All elements visible
- No content cutoff

**Status**: [ ]

---

### 32. Tablet (iPad)

**Test Steps**:
1. Select "iPad" in DevTools
2. Test in portrait and landscape

**Expected Result**:
- Two-column layout on landscape (768px+)
- Comfortable spacing
- Audio players side-by-side in results

**Status**: [ ]

---

### 33. Desktop (1024px+)

**Test Steps**:
1. Resize browser to 1024px width
2. Test at various widths up to 1920px

**Expected Result**:
- Content centered, max-width 1024px
- Generous spacing
- Optimal reading width

**Status**: [ ]

---

## Browser Compatibility Testing

### 34. Chrome (Latest)

**Test Steps**:
1. Open in Chrome 90+
2. Complete full workflow

**Expected Result**:
- All features work
- No console errors
- Smooth performance

**Status**: [ ]

---

### 35. Firefox (Latest)

**Test Steps**:
1. Open in Firefox 88+
2. Complete full workflow

**Expected Result**:
- Same as Chrome
- CSS custom properties work
- ES6 modules load correctly

**Status**: [ ]

---

### 36. Safari (Latest)

**Test Steps**:
1. Open in Safari 14+
2. Complete full workflow

**Expected Result**:
- Same as Chrome/Firefox
- Audio playback works
- Drag-and-drop works

**Status**: [ ]

---

### 37. Edge (Latest)

**Test Steps**:
1. Open in Edge 90+
2. Complete full workflow

**Expected Result**:
- Same as Chrome (Chromium-based)

**Status**: [ ]

---

## Performance Testing

### 38. Lighthouse Audit

**Test Steps**:
1. Open Chrome DevTools → Lighthouse
2. Run audit (Performance, Accessibility, Best Practices)

**Expected Result**:
- Performance: 90+
- Accessibility: 95+
- Best Practices: 90+
- SEO: 90+

**Status**: [ ]

---

### 39. Page Load Speed

**Test Steps**:
1. Open DevTools → Network tab
2. Disable cache
3. Reload page
4. Measure load time

**Expected Result**:
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.0s
- Total load time: < 2.0s

**Status**: [ ]

---

### 40. Memory Usage

**Test Steps**:
1. Open DevTools → Performance → Memory
2. Complete multiple upload/translate cycles
3. Monitor memory usage

**Expected Result**:
- Memory usage stays reasonable (< 100 MB)
- No memory leaks
- Audio URLs properly revoked

**Status**: [ ]

---

## Security Testing

### 41. XSS Protection

**Test Steps**:
1. Try uploading file named: `<script>alert('XSS')</script>.mp3`
2. Try entering malicious text in transcript: `<img src=x onerror=alert('XSS')>`

**Expected Result**:
- No script execution
- Text displayed as plain text (not HTML)
- File name sanitized

**Status**: [ ]

---

### 42. API Key Exposure

**Test Steps**:
1. Open DevTools → Network tab
2. Upload and transcribe audio
3. Check request headers and body

**Expected Result**:
- No OpenAI API key in frontend code
- No API key in network requests
- All API calls go through backend

**Status**: [ ]

---

### 43. CORS Verification

**Test Steps**:
1. Check Network tab for CORS headers
2. Verify only allowed origins can access API

**Expected Result**:
- CORS headers present
- localhost:3000 allowed
- Other origins blocked

**Status**: [ ]

---

## Integration Testing

### 44. Complete Happy Path

**Test Steps**:
1. Upload Hebrew audio (10 seconds)
2. Review transcription
3. Translate to Russian
4. Generate speech with Onyx voice
5. Download result
6. Play downloaded file

**Expected Result**:
- Entire workflow completes without errors
- Generated audio is in Russian
- Audio quality is good
- File downloads successfully

**Status**: [ ]

---

### 45. Multiple Languages

**Test Steps**:
1. Test Hebrew → Russian
2. Test English → Spanish
3. Test French → German
4. Test Chinese → English

**Expected Result**:
- All language pairs work
- Translations are accurate
- TTS generates correct language

**Status**: [ ]

---

### 46. Different Voices

**Test Steps**:
1. Generate same text with all 6 voices
2. Compare audio characteristics

**Expected Result**:
- Each voice sounds distinct
- All voices are clear and natural
- Voice selection is respected

**Status**: [ ]

---

### 47. Long Text Handling

**Test Steps**:
1. Transcribe long audio (5+ minutes)
2. Translate long text (10,000+ characters)

**Expected Result**:
- Long text handled correctly
- No truncation
- Performance remains acceptable
- Character count accurate

**Status**: [ ]

---

## Edge Cases

### 48. Empty Transcript

**Test Steps**:
1. Upload audio with silence
2. Or clear transcript textarea
3. Try to translate

**Expected Result**:
- Error message: "No text to translate"
- No API call made

**Status**: [ ]

---

### 49. Same Source and Target Language

**Test Steps**:
1. Set source: English
2. Set target: English
3. Translate and generate

**Expected Result**:
- Translation completes (even if text unchanged)
- TTS generates English audio
- No error (backend handles it)

**Status**: [ ]

---

### 50. Rapid Button Clicks

**Test Steps**:
1. Upload file
2. Rapidly click "Translate & Generate Speech" multiple times

**Expected Result**:
- Only one request sent
- Button disabled during processing
- No duplicate API calls

**Status**: [ ]

---

## Summary

**Total Tests**: 50

**Passed**: _____ / 50

**Failed**: _____ / 50

**Blocked**: _____ / 50

**Notes**:
_Add any additional observations or issues here_

---

## Test Environment

- **Date**: ___________
- **Tester**: ___________
- **Backend Version**: v1
- **Frontend Version**: Phase 3
- **Browser**: ___________
- **OS**: ___________
- **Screen Resolution**: ___________

---

## Critical Issues Found

1. _Issue description_
   - **Severity**: High/Medium/Low
   - **Steps to reproduce**: ...
   - **Expected**: ...
   - **Actual**: ...

2. _Issue description_
   - ...

---

## Sign-off

- [ ] All critical tests passed
- [ ] All accessibility tests passed
- [ ] All browsers tested
- [ ] Documentation reviewed
- [ ] Ready for production

**Signed**: ___________________
**Date**: ___________________
