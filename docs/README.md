# AI Dubbing Studio Documentation

Complete documentation for the AI Dubbing Studio application - a web-based tool for automated audio dubbing using OpenAI's AI capabilities.

## Quick Links

- [Quick Start Guide](development/QUICK_START.md) - Get up and running in 5 minutes
- [API Contract](api/API_CONTRACT.md) - Backend API specification
- [Architecture Diagram](architecture/ARCHITECTURE_DIAGRAM.md) - System architecture overview
- [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md) - Production deployment instructions

## Documentation Structure

### Development
Essential guides for developers working on the project:

- **[Quick Start Guide](development/QUICK_START.md)** - Setup instructions and first steps
- **[Claude Instructions](development/CLAUDE_INSTRUCTIONS.md)** - Working with Claude Code assistant
- **[Testing Guide](development/TESTING_GUIDE.md)** - Running and writing tests (consolidated)

### Architecture
System design and technical architecture:

- **[Architecture Diagram](architecture/ARCHITECTURE_DIAGRAM.md)** - Complete system design, data flow, and component interactions

### API
Backend API documentation:

- **[API Contract](api/API_CONTRACT.md)** - RESTful API specification with endpoints, schemas, and examples

### Deployment
Production deployment documentation:

- **[Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions for production environments

### Implementation
Detailed implementation documentation for specific components:

- **[Frontend Implementation](implementation/FRONTEND_IMPLEMENTATION.md)** - Frontend architecture, state management, and component structure
- **[Frontend Test Implementation](implementation/FRONTEND_TEST_IMPLEMENTATION.md)** - Frontend test coverage and testing strategies

### Reference
External API documentation and reference materials:

- **[OpenAI API Documentation](reference/openai-api/)** - Reference materials for OpenAI APIs
  - [Audio API Reference](reference/openai-api/audio-openai-api-reference.md)
  - [Speech-to-Text API](reference/openai-api/speech-to-text-openai-api.md)
  - [Text-to-Speech API](reference/openai-api/text-to-speech-openai-api.md)
  - [Using GPT-5.1](reference/openai-api/using-gpt-5-1-openai-api.md)

### History
Historical project documentation and milestone reports:

This section contains completion reports and milestone documentation from the development process:

- [Phase 1 Completion](history/PHASE_1_COMPLETION.md)
- [Phase 2 Complete](history/PHASE_2_COMPLETE.md)
- [Phase 4 Completion](history/PHASE_4_COMPLETION.md)
- [Workstream 3 Completion](history/WORKSTREAM_3_COMPLETION.md)
- [Critical Fixes Implemented](history/CRITICAL_FIXES_IMPLEMENTED.md)
- [Final Project Summary](history/FINAL_PROJECT_SUMMARY.md)
- [Testing Checklist](history/TESTING_CHECKLIST.md)
- [Testing Files Manifest](history/TESTING_FILES_MANIFEST.md)
- [Testing Quick Start](history/TESTING_QUICK_START.md)
- [Testing Summary](history/TESTING_SUMMARY.md)

## Getting Started

1. Start with the **[Quick Start Guide](development/QUICK_START.md)** to set up your development environment
2. Review the **[Architecture Diagram](architecture/ARCHITECTURE_DIAGRAM.md)** to understand the system design
3. Consult the **[API Contract](api/API_CONTRACT.md)** when working with backend endpoints
4. Use the **[Claude Instructions](development/CLAUDE_INSTRUCTIONS.md)** when working with Claude Code

## Contributing

When adding new documentation:

1. Place it in the appropriate subdirectory
2. Update this README.md with a link
3. Follow the existing markdown formatting conventions
4. Include code examples where applicable

## Project Structure

```
docs/
├── README.md (this file)
├── architecture/      # System design and architecture
├── api/              # API documentation
├── development/      # Developer guides
├── deployment/       # Deployment instructions
├── implementation/   # Implementation details
├── history/         # Historical milestone reports
└── reference/       # External reference materials
```
