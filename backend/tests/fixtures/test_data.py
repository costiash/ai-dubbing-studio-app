"""Test data constants for backend tests."""

# Audio file formats
VALID_AUDIO_EXTENSIONS = [".mp3", ".ogg", ".wav", ".m4a"]
INVALID_AUDIO_EXTENSIONS = [".txt", ".pdf", ".jpg", ".exe", ".zip"]

# MIME types
VALID_AUDIO_MIME_TYPES = [
    "audio/mpeg",
    "audio/ogg",
    "audio/wav",
    "audio/x-m4a",
    "audio/mp4",
]
INVALID_AUDIO_MIME_TYPES = [
    "text/plain",
    "application/pdf",
    "image/jpeg",
    "video/mp4",
]

# File sizes
MAX_FILE_SIZE_BYTES = 26214400  # 25 MB
LARGE_FILE_SIZE_BYTES = MAX_FILE_SIZE_BYTES + 1000

# Sample texts
SAMPLE_TRANSCRIPTIONS = [
    "Hello, this is a test transcription.",
    "The quick brown fox jumps over the lazy dog.",
    "Welcome to the AI dubbing studio application.",
    "This is a longer transcription with multiple sentences. It includes various words and phrases. The purpose is to test the system comprehensively.",
]

SAMPLE_TRANSLATIONS = {
    "en_to_es": {
        "source": "Hello, how are you?",
        "target": "Hola, ¿cómo estás?",
        "source_lang": "English",
        "target_lang": "Spanish",
    },
    "en_to_fr": {
        "source": "Good morning",
        "target": "Bonjour",
        "source_lang": "English",
        "target_lang": "French",
    },
    "es_to_en": {
        "source": "¿Dónde está el baño?",
        "target": "Where is the bathroom?",
        "source_lang": "Spanish",
        "target_lang": "English",
    },
}

# Language codes
SUPPORTED_LANGUAGES = [
    "English",
    "Spanish",
    "French",
    "German",
    "Italian",
    "Portuguese",
    "Russian",
    "Japanese",
    "Chinese",
    "Korean",
]

# TTS voices
VALID_TTS_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
INVALID_TTS_VOICES = ["invalid", "unknown", "test"]

# TTS models
VALID_TTS_MODELS = ["tts-1", "tts-1-hd"]
INVALID_TTS_MODELS = ["tts-2", "invalid-model"]

# OpenAI models
TRANSCRIPTION_MODEL = "gpt-4o-transcribe"
TRANSLATION_MODEL = "gpt-5.1"

# Error messages
ERROR_MESSAGES = {
    "file_validation": "Invalid file extension",
    "audio_processing": "Audio conversion failed",
    "transcription": "Transcription failed",
    "translation": "Translation failed",
    "tts": "TTS generation failed",
    "openai_api": "OpenAI API error",
}

# Special characters for testing
SPECIAL_CHARACTERS = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`¡¿áéíóúñü中文日本語한국어"

# Path traversal attempts (for security testing)
PATH_TRAVERSAL_ATTEMPTS = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32",
    "../../../../../../../../etc/shadow",
    ".env",
    "../.env",
]

# XSS attempts (for security testing)
XSS_ATTEMPTS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert('xss')>",
    "javascript:alert('xss')",
    "<svg onload=alert('xss')>",
]

# SQL injection attempts (for security testing)
SQL_INJECTION_ATTEMPTS = [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "1' UNION SELECT * FROM users--",
]
