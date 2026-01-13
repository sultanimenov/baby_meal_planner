# Tasks: Infant Meal Planner (Web)

**Input**: Design documents from `/specs/001-infant-meal-planner/`  
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/openapi.yaml, research.md

**Tests**: Tests included for safety-critical validators and planner graph (per constitution requirement IV).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US8) from spec.md

## Path Conventions

- **Backend**: `backend/app/` (Python/FastAPI)
- **Frontend**: `frontend/src/` (Next.js/TypeScript)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize monorepo structure with both backend and frontend projects

- [ ] T001 Create root project structure with backend/ and frontend/ directories
- [ ] T002 [P] Initialize backend Python project with pyproject.toml and requirements.txt in backend/
- [ ] T003 [P] Initialize frontend Next.js project with TypeScript in frontend/
- [ ] T004 [P] Create docker-compose.yml with postgres service at project root
- [ ] T005 [P] Create .env.example with all required environment variables at project root
- [ ] T006 [P] Configure ruff + black for Python formatting in backend/pyproject.toml
- [ ] T007 [P] Configure eslint + prettier for TypeScript in frontend/
- [ ] T008 [P] Install shadcn/ui and configure TailwindCSS in frontend/
- [ ] T009 Create README.md with setup instructions at project root

**Checkpoint**: Project structure ready, both projects can run independently

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Create FastAPI app entry point in backend/app/main.py
- [ ] T011 [P] Create config module with Pydantic settings in backend/app/core/config.py
- [ ] T012 [P] Create database module with async session in backend/app/core/database.py
- [ ] T013 Setup Alembic migrations in backend/alembic/
- [ ] T014 [P] Create User model with fastapi-users in backend/app/models/user.py
- [ ] T015 [P] Create FoodItem model in backend/app/models/food_item.py
- [ ] T016 [P] Create Recipe model in backend/app/models/recipe.py
- [ ] T017 Generate initial Alembic migration for User, FoodItem, Recipe tables
- [ ] T018 [P] Create seed data loader in backend/app/seed.py
- [ ] T019 [P] Create foods.json seed file with ~50 food items in backend/seed/foods.json
- [ ] T020 [P] Create recipes.json seed file with ~20 recipes in backend/seed/recipes.json
- [ ] T021 [P] Create bootstrap_seeds.py script in backend/scripts/bootstrap_seeds.py
- [ ] T022 [P] Create API client module in frontend/src/lib/api.ts
- [ ] T023 [P] Create Zod schemas for API types in frontend/src/lib/schemas.ts
- [ ] T024 [P] Create auth utilities in frontend/src/lib/auth.ts
- [ ] T025 Create root layout with providers in frontend/src/app/layout.tsx

**Checkpoint**: Foundation ready - database running, seeds loaded, frontend scaffolded

---

## Phase 3: User Story 1 - Account Creation & Baby Profile Setup (P1) 🎯 MVP

**Goal**: User can sign up, log in, and create a baby profile

**Independent Test**: Sign up with email/password → complete baby profile form → reach dashboard

### Backend Implementation (US1)

- [ ] T026 [US1] Configure fastapi-users with JWT auth in backend/app/api/auth.py
- [ ] T027 [US1] Create BabyProfile model in backend/app/models/baby_profile.py
- [ ] T028 [US1] Generate Alembic migration for baby_profiles table
- [ ] T029 [P] [US1] Create profile Pydantic schemas in backend/app/schemas/profile.py
- [ ] T030 [US1] Create ProfileService in backend/app/services/profile_service.py
- [ ] T031 [US1] Create profile API endpoints in backend/app/api/profiles.py
- [ ] T032 [US1] Add DELETE endpoint for profile deletion with cascade in backend/app/api/profiles.py
- [ ] T033 [US1] Register auth and profile routers in backend/app/main.py

### Frontend Implementation (US1)

- [ ] T034 [P] [US1] Create landing page in frontend/src/app/(public)/page.tsx
- [ ] T035 [P] [US1] Create login page in frontend/src/app/(public)/login/page.tsx
- [ ] T036 [P] [US1] Create signup page in frontend/src/app/(public)/signup/page.tsx
- [ ] T037 [P] [US1] Create forgot-password page in frontend/src/app/(public)/forgot-password/page.tsx
- [ ] T038 [P] [US1] Create reset-password page in frontend/src/app/(public)/reset-password/page.tsx
- [ ] T039 [US1] Create auth layout wrapper in frontend/src/app/(auth)/layout.tsx
- [ ] T040 [US1] Create useAuth hook in frontend/src/hooks/use-auth.ts
- [ ] T041 [US1] Create onboarding page in frontend/src/app/(auth)/onboarding/page.tsx
- [ ] T042 [P] [US1] Create BabyProfileForm component in frontend/src/components/forms/BabyProfileForm.tsx
- [ ] T043 [US1] Create dashboard redirect logic (no profile → onboarding) in frontend/src/app/(auth)/page.tsx

**Checkpoint**: User Story 1 complete - users can sign up, create profile, reach dashboard

---

## Phase 4: User Story 2 - Generate a Safe Meal Plan (P1) 🎯 MVP

**Goal**: User can generate a 3-day or 7-day meal plan with safety validation

**Independent Test**: Request plan → see progress → view validated plan with recipes

### Safety Rules (US2) - MUST BE TESTED

- [ ] T044 [P] [US2] Create safety rules module in backend/app/rules/__init__.py
- [ ] T045 [P] [US2] Implement honey_under_12m rule in backend/app/rules/safety.py
- [ ] T046 [P] [US2] Implement choking_hazards rule in backend/app/rules/safety.py
- [ ] T047 [P] [US2] Implement avoid_list rule in backend/app/rules/avoid_list.py
- [ ] T048 [P] [US2] Implement meal_slots_valid rule in backend/app/rules/validators.py
- [ ] T049 [US2] Create unit tests for safety rules in backend/tests/unit/rules/test_safety.py
- [ ] T050 [US2] Create unit tests for avoid_list in backend/tests/unit/rules/test_avoid_list.py

### Planner Graph (US2)

- [ ] T051 [US2] Create PlannerState Pydantic model in backend/app/planner/state.py
- [ ] T052 [US2] Create LLM prompt templates in backend/app/planner/prompts.py
- [ ] T053 [US2] Create web search module in backend/app/planner/search.py
- [ ] T054 [US2] Implement load_context node in backend/app/planner/nodes.py
- [ ] T055 [US2] Implement retrieve_seeds node in backend/app/planner/nodes.py
- [ ] T056 [US2] Implement search_recipes node in backend/app/planner/nodes.py
- [ ] T057 [US2] Implement generate_draft node in backend/app/planner/nodes.py
- [ ] T058 [US2] Implement validate_plan node in backend/app/planner/nodes.py
- [ ] T059 [US2] Implement repair_plan node in backend/app/planner/nodes.py
- [ ] T060 [US2] Implement derive_artifacts node in backend/app/planner/nodes.py
- [ ] T061 [US2] Implement persist_plan node in backend/app/planner/nodes.py
- [ ] T062 [US2] Create LangGraph definition in backend/app/planner/graph.py
- [ ] T063 [US2] Create contract test for planner graph in backend/tests/contract/test_planner.py
- [ ] T064 [US2] Create integration test for repair loop with mocked LLM in backend/tests/integration/test_repair_loop.py

### Backend API (US2)

- [ ] T065 [US2] Create MealPlan model in backend/app/models/meal_plan.py
- [ ] T066 [US2] Generate Alembic migration for meal_plans table
- [ ] T067 [P] [US2] Create plan Pydantic schemas in backend/app/schemas/plan.py
- [ ] T068 [US2] Create PlanService in backend/app/services/plan_service.py
- [ ] T069 [US2] Create plan API endpoints in backend/app/api/plans.py
- [ ] T070 [US2] Register plans router in backend/app/main.py

### Frontend (US2)

- [ ] T071 [P] [US2] Create plan request form in frontend/src/app/(auth)/plan/new/page.tsx
- [ ] T072 [P] [US2] Add WHO meal frequency guidance display to plan request form in frontend/src/components/plan/MealFrequencyGuidance.tsx
- [ ] T073 [P] [US2] Create PlanGenerationProgress component in frontend/src/components/plan/PlanGenerationProgress.tsx
- [ ] T074 [US2] Create plan view page in frontend/src/app/(auth)/plan/[id]/page.tsx
- [ ] T075 [P] [US2] Create PlanDayCard component in frontend/src/components/plan/PlanDayCard.tsx
- [ ] T076 [P] [US2] Create MealCard component in frontend/src/components/plan/MealCard.tsx
- [ ] T077 [P] [US2] Create SafetyBadge component in frontend/src/components/plan/SafetyBadge.tsx

**Checkpoint**: User Story 2 complete - users can generate validated meal plans

---

## Phase 5: User Story 3 - Review and Export Shopping List (P2)

**Goal**: User can view shopping list and share it

**Independent Test**: View plan → click export → see grouped list → share via native share

### Backend (US3)

- [ ] T078 [US3] Add shopping list derivation to derive_artifacts in backend/app/planner/nodes.py
- [ ] T079 [US3] Add prep_suggestions derivation to derive_artifacts in backend/app/planner/nodes.py
- [ ] T080 [US3] Add meal swap endpoint to plans API in backend/app/api/plans.py

### Frontend (US3)

- [ ] T081 [P] [US3] Create ShoppingList component in frontend/src/components/plan/ShoppingList.tsx
- [ ] T082 [P] [US3] Create ShoppingListItem component in frontend/src/components/plan/ShoppingListItem.tsx
- [ ] T083 [P] [US3] Create PrepSuggestions component in frontend/src/components/plan/PrepSuggestions.tsx
- [ ] T084 [US3] Add share functionality using Web Share API in frontend/src/components/plan/ShoppingList.tsx
- [ ] T085 [US3] Create MealSwapModal component in frontend/src/components/plan/MealSwapModal.tsx
- [ ] T086 [US3] Integrate shopping list and swap into plan view page

**Checkpoint**: User Story 3 complete - users can export and share shopping lists

---

## Phase 6: User Story 4 - Daily Meal Logging (P2)

**Goal**: User can log meal outcomes from Today view

**Independent Test**: View Today → see meals → log ate/partial/refused → see updated status

### Backend (US4)

- [ ] T087 [US4] Create MealLog model in backend/app/models/logs.py
- [ ] T088 [US4] Generate Alembic migration for meal_logs table
- [ ] T089 [P] [US4] Create log Pydantic schemas in backend/app/schemas/logs.py
- [ ] T090 [US4] Create LogService in backend/app/services/log_service.py
- [ ] T091 [US4] Create meal log API endpoints in backend/app/api/logs.py
- [ ] T092 [US4] Register logs router in backend/app/main.py

### Frontend (US4)

- [ ] T093 [US4] Create Today page in frontend/src/app/(auth)/today/page.tsx
- [ ] T094 [P] [US4] Create TodayMealCard component in frontend/src/components/logging/TodayMealCard.tsx
- [ ] T095 [P] [US4] Create MealLogModal component in frontend/src/components/logging/MealLogModal.tsx
- [ ] T096 [US4] Add meal log submission and status update to Today page

**Checkpoint**: User Story 4 complete - users can log meals in under 15 seconds

---

## Phase 7: User Story 5 - Reaction Logging (P2)

**Goal**: User can log suspected reactions with symptoms and foods

**Independent Test**: Access reaction form → enter symptoms → select foods → save → view in history

### Backend (US5)

- [ ] T097 [US5] Create ReactionLog model in backend/app/models/logs.py
- [ ] T098 [US5] Generate Alembic migration for reaction_logs table
- [ ] T099 [US5] Add reaction log endpoints to logs API in backend/app/api/logs.py

### Frontend (US5)

- [ ] T100 [P] [US5] Create ReactionLogForm component in frontend/src/components/logging/ReactionLogForm.tsx
- [ ] T101 [P] [US5] Create FoodSelector component in frontend/src/components/logging/FoodSelector.tsx
- [ ] T102 [US5] Create reaction history page in frontend/src/app/(auth)/history/reactions/page.tsx
- [ ] T103 [P] [US5] Create ReactionCard component in frontend/src/components/logging/ReactionCard.tsx

**Checkpoint**: User Story 5 complete - users can log and view reactions

---

## Phase 8: User Story 6 - Food History and Preferences View (P3)

**Goal**: User can view introduced foods with like/refuse counts

**Independent Test**: View food history → see all introduced foods → click food → see stats

### Backend (US6)

- [ ] T104 [US6] Create introduced foods endpoint in backend/app/api/logs.py
- [ ] T105 [US6] Add preference ratio calculation to LogService

### Frontend (US6)

- [ ] T106 [US6] Create food history page in frontend/src/app/(auth)/history/foods/page.tsx
- [ ] T107 [P] [US6] Create IntroducedFoodCard component in frontend/src/components/history/IntroducedFoodCard.tsx
- [ ] T108 [P] [US6] Create FoodDetailModal component in frontend/src/components/history/FoodDetailModal.tsx
- [ ] T109 [US6] Add sorting controls to food history page

**Checkpoint**: User Story 6 complete - users can view food preferences

---

## Phase 9: User Story 7 - Adaptive Plan Generation (P3)

**Goal**: New plans favor liked foods and avoid refused foods

**Independent Test**: Log several meal outcomes → generate new plan → verify liked foods appear more

### Backend (US7)

- [ ] T110 [US7] Add history_summary computation to load_context node in backend/app/planner/nodes.py
- [ ] T111 [US7] Update generate_draft prompt to use history_summary in backend/app/planner/prompts.py
- [ ] T112 [US7] Add allergen introduction gap logic to search_recipes in backend/app/planner/search.py
- [ ] T113 [US7] Create integration test for adaptive generation in backend/tests/integration/test_adaptive.py

**Checkpoint**: User Story 7 complete - plans adapt to user preferences

---

## Phase 10: User Story 8 - Profile Editing (P3)

**Goal**: User can edit baby profile and see regeneration prompt

**Independent Test**: Edit feeding style → save → see notification about regenerating plan

### Backend (US8)

- [ ] T114 [US8] Add PUT endpoint for profile updates in backend/app/api/profiles.py
- [ ] T115 [US8] Add profile change detection to PlanService

### Frontend (US8)

- [ ] T116 [US8] Create profile edit page in frontend/src/app/(auth)/profile/edit/page.tsx
- [ ] T117 [P] [US8] Create ProfileEditForm component in frontend/src/components/forms/ProfileEditForm.tsx
- [ ] T118 [US8] Add regeneration notification to plan view when profile changed

**Checkpoint**: User Story 8 complete - users can edit profiles

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements across all user stories

- [ ] T119 [P] Add error boundaries to all pages in frontend/
- [ ] T120 [P] Add loading states to all async operations in frontend/
- [ ] T121 [P] Add CORS configuration for production in backend/app/main.py
- [ ] T122 Create Dockerfile for backend in backend/Dockerfile
- [ ] T123 [P] Add health check endpoint in backend/app/api/health.py
- [ ] T124 Update README.md with complete setup and deployment instructions
- [ ] T125 Run quickstart.md validation to verify all flows work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational completion
  - US1 and US2 can run in parallel (both P1)
  - US3, US4, US5 can start after US2 (need plans/logging)
  - US6, US7, US8 can start after US4 (need meal logs)
- **Polish (Phase 11)**: After all user stories

### User Story Dependencies

```
US1 (Auth + Profile) ──┬──► US2 (Plan Generation)
                       │          │
                       │          ├──► US3 (Shopping List)
                       │          │
                       │          └──► US4 (Meal Logging) ──► US6 (Food History)
                       │                     │                      │
                       │                     └──► US5 (Reactions)   └──► US7 (Adaptive)
                       │
                       └──► US8 (Profile Edit)
```

### Parallel Opportunities

**Phase 2 (Foundational)**:
```bash
# All models can be created in parallel:
T014, T015, T016  # User, FoodItem, Recipe models
T019, T020, T021  # Seed data files
T022, T023, T024  # Frontend lib modules
```

**Phase 4 (US2 - Plan Generation)**:
```bash
# Safety rules are independent:
T045, T046, T047, T048  # All rule implementations
# Frontend components are independent:
T071, T073, T075, T076, T077  # Plan UI components
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Auth + Profile)
4. Complete Phase 4: US2 (Plan Generation)
5. **STOP and VALIDATE**: Test full flow end-to-end
6. Deploy MVP

### Incremental Delivery

| Milestone | User Stories | Value Delivered |
|-----------|--------------|-----------------|
| MVP | US1, US2 | Sign up, generate safe meal plans |
| +Actionable | US3 | Export shopping list |
| +Daily Use | US4, US5 | Log meals and reactions |
| +Insights | US6 | View food preferences |
| +Smart | US7, US8 | Adaptive plans, profile editing |

---

## Notes

- [P] = different files, no dependencies on incomplete tasks
- [USn] = task belongs to user story n
- Run seed data (T018-T021) before testing plan generation
- Safety rules (T045-T050) are constitution-required tests
- Contract test (T063) verifies planner graph output schema

