<!--
  Sync Impact Report
  ==================
  Version change: N/A → 1.0.0 (initial ratification)
  
  Added sections:
    - I. Code Quality & Design
    - II. Architecture Constraints
    - III. Security & Privacy
    - IV. Testing & Reliability
    - V. Style & Repo Conventions
    - VI. Change Discipline
    - Governance
  
  Templates requiring updates:
    ✅ plan-template.md - Constitution Check section compatible
    ✅ spec-template.md - No changes needed
    ✅ tasks-template.md - No changes needed
  
  Follow-up TODOs: None
-->

# Baby Meal Planner Constitution

## Core Principles

### I. Code Quality & Design

Apply SOLID principles with emphasis on:

- **Single Responsibility**: Each module/class/function MUST have one clear purpose
- **Separation of Concerns**: Clear boundaries between routes, services, repositories, rules, and planner graph
- **Modular Design**: Components MUST be independently testable with explicit interfaces
- **Dependency Inversion**: Business logic MUST NOT depend on frameworks directly; use abstractions

Implementation rules:

- Prefer small, pure functions for rule/validation logic (deterministic, unit-testable)
- Enforce clear naming conventions and type hints (Python: full typing, TypeScript: strict mode)
- Use schema-first validation for all data boundaries

### II. Architecture Constraints

LLM integration boundaries (NON-NEGOTIABLE):

- LLM-generated code MUST NEVER write directly to database without validation
- All LLM outputs MUST be structured (Pydantic for Python, Zod for TypeScript) and validated before use
- Deterministic safety validation is MANDATORY before persisting or displaying meal plans
- Safety rules MUST run as a separate validation step, not embedded in LLM prompts

LangGraph node design:

- Nodes MUST be composable with explicit side-effect boundaries
- IO operations (DB, network) MUST occur at graph edges only
- Pure transformations inside nodes where possible
- State transitions MUST be explicit and logged

### III. Security & Privacy

Secure-by-default patterns (NON-NEGOTIABLE):

- Input validation MUST occur at all system boundaries (API endpoints, form submissions, LLM outputs)
- No secrets in code; environment variables only via `.env` files (never committed)
- Least privilege principle: auth required for all user data endpoints
- Session management MUST use secure, httpOnly cookies or secure token storage

Baby profile data handling:

- Treat all baby profile data as sensitive PII
- Minimize data collection to essential fields only
- Avoid logging sensitive content (baby names, DOB, health data); redact where needed
- Data deletion MUST cascade properly on profile deletion

### IV. Testing & Reliability

Required test coverage:

- **Unit tests**: All deterministic rules and validators MUST have unit tests
- **Contract tests**: Planner graph MUST have contract tests verifying schema-valid output
- **Integration tests**: LLM repair loop behavior MUST be tested with mocked responses

Test quality rules:

- Add fixtures for regression tests; avoid flaky tests (no timing dependencies)
- Mock external services (LLM APIs) in tests; never call production APIs in test runs
- Error handling MUST include clear user-facing messages
- Never swallow exceptions silently; log and surface appropriately

### V. Style & Repo Conventions

Python standards:

- Formatting: ruff + black (line length 88)
- Type checking: mypy-friendly typing on all public functions
- Pydantic models in `schemas/`; SQLAlchemy/DB models in `models/`
- Use `services/` for business logic, `api/` for route handlers

TypeScript standards:

- Formatting: eslint + prettier
- Runtime validation: Zod for all external data
- Components in `components/`; pages in `pages/` or `app/`

File organization:

- No large files: prefer splitting by feature/module; keep files under 300 lines
- Document public APIs and key modules with short docstrings (not verbose)
- README MUST include setup instructions and environment variable list

### VI. Change Discipline

Implementation workflow:

- When implementing a feature, update relevant docs (spec/plan/README) if behavior changes
- Keep PR-sized changes; avoid unrelated refactors in the same commit
- Each commit SHOULD pass linting and existing tests

Decision making:

- If uncertain, prefer the simplest working design that preserves the above rules
- Complexity MUST be justified in PR description or plan.md
- New dependencies require justification (1-2 bullets explaining why needed)

## Governance

This constitution establishes non-negotiable standards for the Baby Meal Planner project.

Amendment process:

1. Propose change with rationale in PR description
2. Update constitution version following semver (MAJOR: breaking principle change, MINOR: new principle, PATCH: clarification)
3. All active contributors MUST acknowledge significant changes

Compliance:

- All PRs MUST be verified against constitution principles before merge
- Violations MUST be documented and justified in Complexity Tracking section of plan.md
- Use this constitution as the source of truth for architectural decisions

**Version**: 1.0.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-12
