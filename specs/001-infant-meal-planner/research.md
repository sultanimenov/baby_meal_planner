# Research: Infant Meal Planner

**Date**: 2026-01-12  
**Status**: Complete

## Technology Decisions

### 1. Backend Framework: FastAPI

**Decision**: Use FastAPI with Python 3.11

**Rationale**:
- Native async support for LLM API calls (non-blocking during generation)
- First-class Pydantic integration (schema validation at boundaries)
- Automatic OpenAPI spec generation
- Strong typing support aligns with constitution requirements

**Alternatives Considered**:
- Django REST Framework: More batteries included but heavier; async support less mature
- Flask: Simpler but requires more manual setup; no native Pydantic

### 2. Authentication: fastapi-users

**Decision**: Use fastapi-users with JWT (httpOnly cookies)

**Rationale**:
- Production-ready auth out of the box (register, login, reset, verify)
- Supports SQLModel/SQLAlchemy backends
- JWT in httpOnly cookies for web security (no localStorage token exposure)
- Reduces custom auth code (security-sensitive area)

**Alternatives Considered**:
- Custom JWT implementation: More control but higher security risk
- Auth0/Clerk: External dependency; adds latency; overkill for MVP

### 3. Database ORM: SQLModel

**Decision**: Use SQLModel (SQLAlchemy 2.0 wrapper with Pydantic)

**Rationale**:
- Single model definition for DB + API schemas (reduces duplication)
- Type hints enforced at DB layer
- Compatible with Alembic migrations
- Pydantic v2 compatibility

**Alternatives Considered**:
- Pure SQLAlchemy 2.0: More mature but requires separate Pydantic models
- Tortoise ORM: Less ecosystem support; async-only can complicate testing

### 4. LLM Orchestration: LangChain + LangGraph

**Decision**: Use LangChain for LLM wrapper, LangGraph for state machine

**Rationale**:
- LangGraph provides explicit state machine semantics (validate → repair loop)
- Clear separation between LLM calls and deterministic logic
- Structured output support via Pydantic schemas
- LangSmith integration for tracing/debugging (recommended for production)

**Alternatives Considered**:
- Direct OpenAI SDK: Less abstraction but no state machine; harder to implement repair loop
- Instructor library: Good for structured outputs but no graph/flow semantics

### 5. Frontend Framework: Next.js 14 (App Router)

**Decision**: Next.js with App Router, TypeScript, TailwindCSS, shadcn/ui

**Rationale**:
- App Router: Modern React patterns (server components, streaming)
- TypeScript: Type safety across frontend
- TailwindCSS: Rapid UI development, consistent design system
- shadcn/ui: Accessible, customizable components (not a heavy dependency)
- React Hook Form + Zod: Form handling with runtime validation

**Alternatives Considered**:
- Remix: Good DX but smaller ecosystem
- Vite + React: No SSR out of box; less suited for SEO landing page
- SvelteKit: Smaller talent pool; TypeScript support less mature

### 6. Recipe Data Strategy: Curated Seed Library

**Decision**: Ground LLM on ~50 curated recipes seeded in DB (not pure AI generation)

**Rationale**:
- Deterministic validation is more reliable when recipes are pre-vetted
- Allergen tags, safety notes pre-populated accurately
- LLM selects/combines from known-safe recipes rather than inventing
- Reduces hallucination risk; easier to test

**Alternatives Considered**:
- Pure AI recipe generation: Higher creativity but unpredictable safety
- External recipe API: Dependency on third party; format inconsistency

### 7. LLM Provider

**Decision**: OpenAI GPT-4o-mini (default), configurable via env var

**Rationale**:
- Cost-effective for structured output tasks
- Fast response times (<10s typical)
- Good at following JSON schema constraints
- Can upgrade to GPT-4o if quality issues arise

**Alternatives Considered**:
- Claude: Strong reasoning but API stability concerns
- Local LLM (Ollama): Privacy benefits but slower; harder to deploy

## Resolved Clarifications

| Question | Resolution |
|----------|------------|
| Recipe source | Curated seed library (50 recipes) + LLM selection/customization |
| Plan generation time | 30s max with progress indicator; retry once on failure |
| AI failure handling | Auto-retry once → show error with manual retry button |
| Shopping list export | In-app display + native share sheet |
| Data retention | Keep all plans indefinitely; delete only with profile |

## Security Considerations

- **Baby data as PII**: Redact names/DOB from logs; use UUIDs in URLs
- **LLM output validation**: Never trust raw LLM output; always Pydantic validate
- **Auth tokens**: JWT in httpOnly cookies; short expiry (15min access, 7d refresh)
- **Rate limiting**: Consider Redis-based rate limiting for plan generation (expensive operation)

## Performance Considerations

- **Plan generation**: Async endpoint with SSE or polling for progress
- **Recipe candidate retrieval**: Index on feeding_style, texture_level for fast filtering
- **Caching**: Consider caching recipe list (rarely changes) in Redis

## Open Items for Implementation

1. **Seed data creation**: Need to create 50 curated recipes with proper tags
2. **LLM prompt tuning**: Draft + repair prompts need iteration
3. **LangSmith setup**: Optional but recommended for debugging

