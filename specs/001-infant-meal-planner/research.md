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
- **Email verification included**: provides `/auth/request-verify-token` and `/auth/verify` endpoints; user model includes `is_verified` field

**Alternatives Considered**:
- Custom JWT implementation: More control but higher security risk
- Auth0/Clerk: External dependency; adds latency; overkill for MVP

**Email Verification Coverage** (FR-001):
- User model: `is_verified` field (managed by fastapi-users)
- Endpoints: `/auth/request-verify-token`, `/auth/verify` (auto-generated)
- T028 (Configure fastapi-users) includes enabling verification flow

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

### 6. Recipe Data Strategy: Hybrid (Seed Library + Web Search)

**Decision**: Small curated seed library (~20 recipes) + runtime web search for variety

**Rationale**:
- Seed library provides reliable baseline for testing and offline fallback
- Web search adds variety, cultural diversity, and fresh content
- Deterministic validation catches any unsafe web content
- Reduces manual curation burden while maintaining safety

**Approach**:
- ~20 core seed recipes (manually reviewed, properly tagged)
- Web search node queries credible infant nutrition sources at plan generation
- LLM structures web results into recipe schema
- All recipes (seed + web) pass through deterministic safety validation

**Credible Sources for Web Search**:
- solidstarts.com - Comprehensive food database with age/texture guidance
- babyledweaning.com - BLW-focused recipes
- feedinglittles.com - Registered dietitian content
- healthychildren.org - AAP (American Academy of Pediatrics) guidance
- nhs.uk/start-for-life - UK NHS weaning guidelines

**Seed Bootstrap Strategy**:
- One-time LLM + web search to generate candidate recipes
- Human review and approval before adding to seed DB
- Focus on: 5 breakfast, 5 lunch, 5 dinner, 5 snack recipes across textures

**Alternatives Considered**:
- 50+ curated recipes only: Too much manual curation burden
- Pure web search: No offline fallback; less testable
- External recipe API: No infant-specific APIs found; format inconsistency

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

1. **Seed data bootstrap**: Run `scripts/bootstrap_seeds.py` to generate candidates, then human review
2. **LLM prompt tuning**: Draft + repair prompts need iteration
3. **LangSmith setup**: Optional but recommended for debugging
4. **Web search integration**: Implement search node with rate limiting and caching

## Bootstrap Seeds Script Design

`scripts/bootstrap_seeds.py` will:

1. **Search credible sources** for infant recipes:
   - Query: "6 month baby puree recipes site:solidstarts.com"
   - Query: "baby led weaning finger foods site:babyledweaning.com"
   - Query: "infant breakfast recipes site:feedinglittles.com"

2. **Extract recipe content** from search results:
   - Fetch page content
   - LLM extracts: title, ingredients, steps, texture level

3. **Structure into Pydantic schema**:
   ```python
   class RecipeCandidate(BaseModel):
       title: str
       source_url: str
       ingredients: list[Ingredient]
       steps: list[str]
       texture_level: Literal["puree", "soft_mash", "finger_food"]
       estimated_prep_minutes: int
       suggested_age_months: int
   ```

4. **Output to `seed/candidates.json`** for human review

5. **Human review workflow**:
   - Review each candidate
   - Add allergen tags manually (LLM may miss)
   - Verify safety notes
   - Move approved to `seed/recipes.json`

**Usage**:
```bash
cd backend
python scripts/bootstrap_seeds.py --count 30 --output seed/candidates.json
# Review candidates.json manually
# Move approved recipes to seed/recipes.json
```

