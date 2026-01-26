# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment
- This is a Windows system without bash/WSL
- Use PowerShell for all terminal commands
- Use Windows-style paths (C:\Dev\...)

## Project Overview

ResumeTry is an Angular 20 web application with a FastAPI serverless backend using Pydantic for model validation to handle API requests.

- Track Job Applications that are submitted to companies.
- Track Notes about things that happen to Job Applications.

## Architecture

- **Frontend**: Angular 20 with standalone components (no NgModules)
- **Backend**: AWS Lambda hosting FastAPI with Pydantic for handling API requests
- **Deployment**: Multi-stage Docker build with Nginx for production serving

### Frontend Structure
```
frontend/src/app/
├── app.component.ts          # Root component
├── app.routes.ts             # Route definitions (provideRouter)
├── main.ts                   # Bootstrap with bootstrapApplication()
├── core/
│   ├── models/               # Interfaces, enums, type definitions
│   └── services/             # Injectable services (HttpClient, signals)
└── features/
    └── applications/         # Job application feature components
        ├── application-list/
        ├── application-detail/
        └── application-form/
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

## Angular 20 Conventions

### Component Architecture
- All components are standalone by default (Angular 20 no longer requires `standalone: true`)
- No NgModules — use `bootstrapApplication()` with provider functions in `main.ts`
- Use `imports: [...]` directly in `@Component` metadata for dependencies (e.g., `ReactiveFormsModule`, `RouterOutlet`)

### Dependency Injection
- Use the `inject()` function instead of constructor injection
- Example: `private readonly service = inject(JobApplicationService);`

### Signals & Reactivity (Stable in Angular 20)
- Use `signal()` for component state (e.g., `isLoading = signal(true)`)
- Use `computed()` for derived state that auto-updates when dependencies change
- Use `.set()` and `.update()` to modify signals
- Read signal values with `()` syntax in both templates and TypeScript (e.g., `isLoading()`)
- `linkedSignal()`, `effect()`, signal-based queries, and signal-based inputs are all stable — use when appropriate
- Signal-based forms are still experimental — continue using `ReactiveFormsModule` for forms

### Template Syntax
- Use built-in control flow: `@if`, `@else`, `@for`, `@switch`, `@case`, `@default`
- Do NOT use structural directives (`*ngIf`, `*ngFor`, `*ngSwitch`) — these are deprecated in Angular 20
- Use `track` with `@for` loops (e.g., `@for (item of items; track item.id)`)
- Template local variable binding: `@if (value(); as alias)` to alias signal reads
- `@defer` / `@placeholder` blocks available for lazy loading sections of templates

### HTTP & Routing
- Use `provideHttpClient(withFetch())` in providers (not `HttpClientModule`)
- Use `provideRouter(routes)` for routing (not `RouterModule`)
- Routes defined as a `const Routes` array exported from `app.routes.ts`

### Testing
- Currently using Karma + Jasmine (Karma is deprecated in Angular 20)
- Angular 20 introduces experimental support for alternative test runners (Vitest, Web Test Runner)

### TypeScript
- TypeScript 5.9 — use modern syntax and features
- Target: ES2022
- Module resolution: `bundler`
- Strict template checking enabled (`strictTemplates`, `strictInjectionParameters`, `strictInputAccessModifiers`)

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