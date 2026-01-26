# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment
- This is a Windows system without bash/WSL
- Use PowerShell for all terminal commands
- Use Windows-style paths (C:\Dev\...)

## Project Overview

ResumeTry is an Angular 18 web application with a FastAPI serverless backend using Pydantic for model validation to handle API requests.

- Track Job Applications that are submitted to companies.
- Track Notes about things that happen to Job Applications.

## Architecture

- **Frontend**: Angular 18 with standalone components (no NgModules)
- **Backend**: AWS Lambda hosting FastAPI with Pydantic for handling API requests
- **Deployment**: Multi-stage Docker build with Nginx for production serving

### Frontend Structure
```
frontend/src/app/
├── app.component.ts     # Root component
├── app.routes.ts        # Standalone routing (currently empty)
└── main.ts              # Bootstrap with provideRouter
```

### Backend Structure
```
backend/app/
├── main.py              # FastAPI app + Lambda handler
├── config.py            # Settings via pydantic-settings
├── routers/
│   ├── health.py        # GET /health
│   └── api_v1.py        # GET /api/v1/ping
├── models/
│   ├── base.py          # Base Pydantic schema
│   ├── responses.py     # Response models
│   ├── enums.py         # ApplicationStatus enum
│   └── job_application.py  # Job application models
└── db/
    └── dynamodb.py      # DynamoDB client and table setup
```

### Key Configuration - Frontend
- TypeScript strict mode enabled
- Nginx configured with security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- SPA routing: all routes serve index.html
- Static assets cached for 1 year

### Key Configuration - Backend
- API docs at /api/docs (Swagger UI)
- CORS configured via RESUMETRY_CORS_ORIGINS env var
- Nginx proxies /api/ to backend:8000

## Code Style

### Frontend
- 2-space indentation
- Single quotes in TypeScript
- UTF-8 encoding
- No ESLint/Prettier configured - follow EditorConfig rules

### Backend
- 4-space indentation (Python standard)
- Single quotes for strings
- Type hints encouraged
- Always use fully parameterized types (e.g., `dict[str, Any]`, `list[str]`) instead of bare `dict` or `list` to avoid Pylance `reportUnknownMemberType` errors
- use datetime.now() instead of datetime.utcnow()