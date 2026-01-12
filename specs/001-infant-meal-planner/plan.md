# Implementation Plan: Infant Meal Planner (Web)

**Branch**: `001-infant-meal-planner` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-infant-meal-planner/spec.md`

## Summary

Build a web app that lets parents sign up/login, create a baby profile, generate AI-powered 3-day/7-day meal plans with deterministic safety validation, export shopping lists, and log meal outcomes/reactions. Uses LangChain + LangGraph (Python) to orchestrate plan generation with a validate-repair loop grounded on a curated recipe library.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**:
- Backend: FastAPI, fastapi-users, SQLModel, Alembic, LangChain, LangGraph, Pydantic v2
- Frontend: Next.js 14 (App Router), TailwindCSS, shadcn/ui, React Hook Form, Zod

**Storage**: PostgreSQL 15+  
**Testing**: pytest (backend), Vitest (frontend)  
**Target Platform**: Web (Linux server for backend, Vercel for frontend)  
**Project Type**: Web application (separate frontend/backend)  
**Performance Goals**: Page load <3s, plan generation <30s with progress indicator  
**Constraints**: Single baby profile per user for v1 (multi-profile supported in spec for future)  
**Scale/Scope**: Single user focus for MVP; ~20 seed recipes + web search augmentation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Code Quality | Pure functions for rules/validation; type hints on all public APIs | ✅ Planned: rules/ module with pure validators |
| II. Architecture | LLM outputs validated via Pydantic/Zod; safety validation before persist/display | ✅ Planned: LangGraph validate node + deterministic rules |
| III. Security | Input validation at boundaries; no secrets in code; auth on user endpoints | ✅ Planned: fastapi-users + Pydantic validation |
| IV. Testing | Unit tests for validators; contract tests for planner graph | ✅ Planned: pytest fixtures for rules + graph contracts |
| V. Style | ruff/black (Python) or eslint/prettier (TS); files <300 lines | ✅ Will enforce via pre-commit hooks |
| VI. Change | Docs updated if behavior changes; no unrelated refactors | ✅ Will follow |

## Project Structure

### Documentation (this feature)

```text
specs/001-infant-meal-planner/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI spec)
└── checklists/          # Quality checklists
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/                 # FastAPI route handlers
│   │   ├── auth.py          # Auth endpoints (fastapi-users)
│   │   ├── profiles.py      # Baby profile CRUD
│   │   ├── plans.py         # Plan generation + retrieval
│   │   └── logs.py          # Meal + reaction logging
│   ├── models/              # SQLModel database models
│   │   ├── user.py
│   │   ├── baby_profile.py
│   │   ├── recipe.py
│   │   ├── food_item.py
│   │   ├── meal_plan.py
│   │   └── logs.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── profile.py
│   │   ├── plan.py
│   │   └── logs.py
│   ├── services/            # Business logic
│   │   ├── profile_service.py
│   │   ├── plan_service.py
│   │   └── log_service.py
│   ├── rules/               # Deterministic validation (pure functions)
│   │   ├── __init__.py
│   │   ├── safety.py        # honey_under_12m, choking_hazards
│   │   ├── avoid_list.py    # allergen/avoid checking
│   │   └── validators.py    # meal_slots_valid, etc.
│   ├── planner/             # LangGraph orchestration
│   │   ├── __init__.py
│   │   ├── graph.py         # Main planner graph definition
│   │   ├── nodes.py         # Graph node implementations
│   │   ├── state.py         # PlannerState Pydantic model
│   │   ├── prompts.py       # LLM prompt templates
│   │   └── search.py        # Web search for recipes (credible sources)
│   ├── core/
│   │   ├── config.py        # Settings from env vars
│   │   ├── database.py      # DB session management
│   │   └── security.py      # Auth helpers
│   └── main.py              # FastAPI app entry point
├── alembic/                 # Database migrations
├── tests/
│   ├── unit/
│   │   └── rules/           # Validator unit tests
│   ├── contract/
│   │   └── test_planner.py  # Graph schema contract tests
│   └── integration/
│       └── test_api.py      # API integration tests
├── seed/                    # Recipe + food item seed data
├── requirements.txt
├── pyproject.toml
└── Dockerfile

frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (public)/        # Landing, login, signup
│   │   │   ├── page.tsx     # Landing
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── (auth)/          # Protected routes
│   │   │   ├── layout.tsx   # Auth check wrapper
│   │   │   ├── onboarding/
│   │   │   ├── today/
│   │   │   ├── plan/
│   │   │   │   ├── new/
│   │   │   │   └── [id]/
│   │   │   └── history/
│   │   │       ├── foods/
│   │   │       └── reactions/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── forms/           # Form components
│   │   ├── plan/            # Plan display components
│   │   └── logging/         # Meal/reaction log components
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── auth.ts          # Auth utilities
│   │   └── schemas.ts       # Zod schemas
│   └── hooks/
│       └── use-auth.ts
├── public/
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js

docker-compose.yml           # postgres + backend
.env.example
README.md
```

**Structure Decision**: Web application with separate backend (FastAPI/Python) and frontend (Next.js/TypeScript). Backend handles all business logic, LLM orchestration, and data persistence. Frontend is a thin client focused on UI/UX.

## High-Level Architecture

### Core Principle: LLM Drafts → Deterministic Validation → Final Plan

We don't rely on the LLM to enforce safety. The flow is:

1. **LLM generates draft plan** as structured JSON referencing recipe IDs from curated library
2. **Deterministic validator** checks rule set (block/warn violations)
3. **If blocked**: LangGraph triggers repair loop (LLM edits minimal parts)
4. **Only validated plans** are persisted and shown to user

### LangGraph Planner State Machine

```
┌─────────────────┐
│  load_context   │ ← Fetch profile, compute age, load history
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│retrieve_seeds   │ ← Filter seed recipes from DB
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ search_recipes  │ ← Web search credible sources (solidstarts, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│generate_draft   │ ← LLM creates plan from seeds + web results
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ validate_plan   │ ← Deterministic rules check
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 [pass]    [block]
    │         │
    │    ┌────┴────┐
    │    │attempt<2│
    │    └────┬────┘
    │    yes  │  no
    │    ┌────┴────┐
    │    ▼         ▼
    │ repair    [fail]
    │    │
    │    └──► validate_plan
    │
    ▼
┌─────────────────┐
│derive_artifacts │ ← Shopping list, prep suggestions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  persist_plan   │ ← Save to DB
└─────────────────┘
```

## Complexity Tracking

> **No constitution violations requiring justification at this time.**

All architectural choices align with constitution principles:
- Pure functions in `rules/` for safety validation
- LLM outputs validated via Pydantic before any DB write
- Separate validation step (not embedded in prompts)
- Clear separation: api/ → services/ → rules/ → planner/
