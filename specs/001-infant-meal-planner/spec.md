# Feature Specification: Infant Meal Planner (Web)

**Feature Branch**: `001-infant-meal-planner`  
**Created**: 2026-01-12  
**Status**: Draft  
**Input**: User description: "Build a web app that helps parents plan and manage complementary feeding meals for a 7-month-old baby. Web-only for v1."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Account Creation & Baby Profile Setup (Priority: P1)

A new parent visits the app landing page and creates an account to start planning meals for their baby. After signup, they complete the onboarding process by creating a baby profile with all necessary preferences. (v1 supports one baby profile per account.)

**Why this priority**: Without authentication and baby profile setup, no other functionality is accessible. This is the foundational entry point for all users.

**Independent Test**: Can be fully tested by signing up with email/password, then completing the baby profile form. Delivers value by establishing the personalized context for meal planning.

**Acceptance Scenarios**:

1. **Given** a visitor on the landing page, **When** they click "Sign Up" and enter valid email/password, **Then** an account is created and they are directed to baby profile creation
2. **Given** a logged-in user with no baby profile, **When** they access any protected page, **Then** they are redirected to the "Create Baby Profile" onboarding form
3. **Given** a user on the onboarding form, **When** they complete all required fields (nickname, DOB, feeding style, meals/day target), **Then** the baby profile is saved and they are directed to the Dashboard
4. **Given** a user on the onboarding form, **When** they submit with missing required fields, **Then** validation errors are displayed and submission is blocked
5. **Given** a returning user with an existing baby profile, **When** they log in, **Then** they are directed to the Dashboard/Today view

---

### User Story 2 - Generate a Safe Meal Plan (Priority: P1)

A parent generates a meal plan for their baby. The system creates a 3-day or 7-day plan that respects the baby's age, feeding style, allergies/avoid list, and dietary preferences. All generated plans pass safety validation before display.

**Why this priority**: Meal plan generation is the core value proposition. Without safe, personalized plans, the app has no primary utility.

**Independent Test**: Can be fully tested by generating a plan and verifying it contains age-appropriate meals, respects avoid list, and includes no blocked items. Delivers value by providing a ready-to-use feeding schedule.

**Acceptance Scenarios**:

1. **Given** a user with a baby profile, **When** they request a 7-day plan with "more variety" style, **Then** a plan with diverse meals is generated and displayed day-by-day
2. **Given** a user with a baby profile, **When** they request a 3-day plan with "simple repeats" style, **Then** a plan with repeated familiar meals is generated
3. **Given** a baby profile with honey on the avoid list, **When** a plan is generated, **Then** no meals contain honey and the plan passes safety validation
4. **Given** a baby under 12 months, **When** any plan is generated, **Then** honey is automatically blocked regardless of user settings (CDC guidance)
5. **Given** a user enables "introduce new foods" toggle, **When** a plan is generated, **Then** new foods are flagged with "NEW" label and common allergens are tagged
6. **Given** a plan contains a common choking hazard ingredient, **When** the plan is displayed, **Then** safe preparation guidance is included for that ingredient
7. **Given** a baby profile with "vegetarian" preference, **When** a plan is generated, **Then** no meat/fish items appear in any meals

---

### User Story 3 - Review and Export Shopping List (Priority: P2)

A parent reviews their generated meal plan, then exports a shopping list grouped by category. They can also view batch-prep suggestions to save time.

**Why this priority**: Once a plan is generated, parents need actionable output. Shopping list export enables execution of the plan in the real world.

**Independent Test**: Can be fully tested by generating a plan and exporting the shopping list. Delivers value by transforming the plan into a practical grocery list.

**Acceptance Scenarios**:

1. **Given** a generated meal plan, **When** user clicks "Export Shopping List", **Then** a list grouped by category (produce, proteins, grains, dairy, etc.) is displayed
2. **Given** a shopping list is displayed, **When** user views it, **Then** items are de-duplicated and quantities are aggregated across all meals
3. **Given** a shopping list, **When** user clicks an item, **Then** they can mark it as "have it" or edit the quantity
4. **Given** a generated plan, **When** user views "Prep Plan", **Then** batch cooking suggestions are displayed (e.g., "cook sweet potato in bulk on Sunday")
5. **Given** a user manually swaps a meal in the plan, **When** they re-export the shopping list, **Then** the list reflects the updated meal

---

### User Story 4 - Daily Meal Logging (Priority: P2)

A parent uses the "Today" view to see scheduled meals, follow recipe steps, and log meal outcomes (ate/partial/refused) with optional notes.

**Why this priority**: Daily interaction drives engagement and builds the data needed to personalize future plans. This is the primary daily touchpoint.

**Independent Test**: Can be fully tested by viewing Today, following a meal recipe, and logging an outcome. Delivers value by tracking feeding progress.

**Acceptance Scenarios**:

1. **Given** a user with an active plan, **When** they visit the Dashboard/Today view, **Then** they see today's meals with recipe steps and texture guidance
2. **Given** a meal on the Today view, **When** user taps "Log", **Then** they can select ate/partial/refused and add optional notes
3. **Given** a user logging a meal, **When** they submit the log, **Then** the meal card updates to show logged status
4. **Given** a user on the Today view, **When** a meal includes a "new food", **Then** it is visually highlighted
5. **Given** a user, **When** they complete a meal log, **Then** the log is saved in under 15 seconds from tap to confirmation

---

### User Story 5 - Reaction Logging (Priority: P2)

A parent notices a potential reaction and logs it with timestamp, symptoms, and suspected food(s) for future reference.

**Why this priority**: Tracking reactions is critical for identifying problematic foods and ensuring baby safety during allergen introduction.

**Independent Test**: Can be fully tested by logging a reaction with symptoms and suspected foods. Delivers value by maintaining a safety record.

**Acceptance Scenarios**:

1. **Given** a logged-in user, **When** they access "Log Reaction", **Then** they can enter timestamp (defaults to now), symptoms (free text), and select suspected food(s) from recently introduced items
2. **Given** a reaction log form, **When** user submits with symptoms and at least one suspected food, **Then** the reaction is saved to the baby's history
3. **Given** existing reaction logs, **When** user views reaction history, **Then** logs are displayed chronologically with all captured details

---

### User Story 6 - Food History and Preferences View (Priority: P3)

A parent views a history of all introduced foods, including like/refuse counts and any logged reactions, to understand their baby's preferences.

**Why this priority**: History provides insight into patterns and supports informed decisions, but is not required for core daily use.

**Independent Test**: Can be fully tested by introducing multiple foods and viewing the history page. Delivers value by visualizing feeding progress.

**Acceptance Scenarios**:

1. **Given** a user with meal history, **When** they view "Introduced Foods", **Then** they see all foods the baby has tried with first-introduced date
2. **Given** the introduced foods view, **When** user clicks a food, **Then** they see like count, refuse count, and any associated reaction logs
3. **Given** foods with multiple outcomes logged, **When** user views the list, **Then** foods are sortable by name, date introduced, or preference ratio

---

### User Story 7 - Adaptive Plan Generation (Priority: P3)

When generating a new plan, the system uses meal log history to prefer liked foods, reduce refused foods, and respect recently introduced items.

**Why this priority**: Personalization improves over time, but first-time users get value from basic plans. This is an enhancement layer.

**Independent Test**: Can be fully tested by logging several meals with outcomes, then generating a new plan and verifying it favors liked foods.

**Acceptance Scenarios**:

1. **Given** a baby has logged "ate" for carrots 5 times, **When** a new plan is generated, **Then** carrots appear more frequently than average
2. **Given** a baby has logged "refused" for peas 3 times in a row, **When** a new plan is generated, **Then** peas appear less frequently or are excluded
3. **Given** "introduce new foods" is enabled, **When** a plan is generated, **Then** new foods not yet introduced are included and labeled
4. **Given** an allergen was introduced in the last 3 days, **When** "introduce new foods" generates a plan, **Then** another new allergen is not introduced until a gap period passes

---

### User Story 8 - Profile Editing (Priority: P3)

A parent updates the baby profile as preferences change (e.g., transition from purée to mixed texture, add new allergies).

**Why this priority**: Profiles evolve over time, but initial setup is the critical path. Editing is a maintenance feature.

**Independent Test**: Can be fully tested by editing feeding style and verifying next generated plan reflects the change.

**Acceptance Scenarios**:

1. **Given** a user on the profile edit page, **When** they change feeding style from "purée" to "mixed", **Then** the change is saved
2. **Given** a user edits baby DOB, **When** they save, **Then** a prompt explains that existing plan may need regeneration
3. **Given** a user adds "eggs" to the avoid list, **When** they generate a new plan, **Then** eggs do not appear in any meals
4. **Given** a mid-week edit to profile, **When** user views current plan, **Then** a notification suggests regenerating for updated preferences

---

### Edge Cases

- **No baby profile**: User logs in but has no baby profile → forced redirection to onboarding before any other feature access
- **Profile deletion**: User can delete a baby profile; requires confirmation; all associated data (plans, logs, reactions) is removed
- **DOB/feeding style change mid-week**: Clear notification explaining plan may be outdated; option to regenerate
- **"Introduce allergens" toggle**: When toggled on/off, existing logs retain their labels; only new plans are affected
- **Ingredient unavailable**: When user marks an ingredient unavailable, suggested substitutions must not violate avoid list or introduce blocked items
- **Manual meal swap**: When user swaps a meal, shopping list recalculates automatically; prep suggestions update if affected
- **Password reset**: User can request password reset via email link
- **Logout**: User can log out from any page; session is cleared
- **Login errors**: Invalid credentials show user-friendly error; locked account after 5 failed attempts with unlock via email
- **AI generation failure**: If plan generation fails, system retries once automatically; if retry fails, user sees friendly error message with "Try Again" button; no partial/corrupt plans are saved

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Authorization**
- **FR-001**: System MUST support email/password registration with email verification
- **FR-002**: System MUST support email/password login with session management
- **FR-003**: System MUST support password reset via email link
- **FR-004**: System MUST block access to all features except landing/auth pages for logged-out users
- **FR-005**: System MUST support secure logout that clears user session

**Baby Profile Management**
- **FR-006**: System MUST collect baby nickname (required), DOB (required), feeding style (required: purée/BLW/mixed), meals per day target (required: 1-3)
- **FR-007**: System MUST collect optional profile data: known allergies, avoid list, dietary preferences (vegetarian/omnivore), cultural cuisine preferences
- **FR-008**: System MUST collect practical constraints: max prep time per day, batch-cook days, pantry staples
- **FR-009**: System MUST support editing all baby profile fields after initial creation
- **FR-010**: System MUST limit to one baby profile per account for v1
- **FR-010a (v2)**: System MUST support multiple baby profiles per account
- **FR-010b (v2)**: System MUST allow users to switch between baby profiles from any screen
- **FR-010c (v2)**: System MUST allow creating additional baby profiles after initial onboarding

**Safety Validation**
- **FR-011**: System MUST block honey and honey-containing items for babies under 12 months (CDC guidance)
- **FR-012**: System MUST flag common choking hazards and require "safe form" preparation guidance
- **FR-013**: System MUST run safety validation on every generated plan before display
- **FR-014**: System MUST never suggest substitutions that violate the avoid list or safety rules
- **FR-015**: System MUST display age-appropriate meal frequency guidance (WHO: 2-3 times/day at 6-8 months) but allow user override

**Meal Plan Generation**
- **FR-016**: System MUST generate meal plans with AI-created recipes tailored to baby's profile (age, feeding style, preferences)
- **FR-016a**: System MUST support 3-day and 7-day plan generation
- **FR-017**: System MUST support plan style selection: "more variety" vs "simple repeats"
- **FR-018**: System MUST support "introduce new foods" toggle that includes and labels new foods in plans
- **FR-019**: System MUST display plans day-by-day with recipe name, ingredients, steps, and texture guidance
- **FR-020**: System MUST highlight "new foods" and tag common allergens in plan display
- **FR-021**: System MUST allow manual meal swaps within a plan
- **FR-022**: System MUST adapt future plans based on logged likes/refuses when history exists

**Shopping & Prep**
- **FR-023**: System MUST generate shopping lists from meal plans, grouped by category
- **FR-024**: System MUST de-duplicate and aggregate quantities across meals in shopping lists
- **FR-025**: System MUST allow editing/marking items in shopping lists
- **FR-025a**: System MUST support sharing shopping list via native share sheet (copy, email, messaging apps)
- **FR-026**: System MUST provide batch cooking/prep suggestions based on plan and user's batch-cook days
- **FR-027**: System MUST update shopping list when meals are swapped

**Meal Logging**
- **FR-028**: System MUST support logging meal outcomes: ate, partial, refused
- **FR-029**: System MUST support optional notes on meal logs
- **FR-030**: System MUST display Today view with current day's meals and recipe details

**Reaction Logging**
- **FR-031**: System MUST support reaction logging with: timestamp, symptoms (free text), suspected food(s)
- **FR-032**: System MUST allow selecting suspected foods from recently introduced items
- **FR-033**: System MUST display reaction history chronologically

**History & Analytics**
- **FR-034**: System MUST display all introduced foods with first-introduced date
- **FR-035**: System MUST display like/refuse counts per food
- **FR-036**: System MUST support sorting introduced foods by name, date, or preference ratio

### Key Entities

- **UserAccount**: Authentication identity containing email, password hash, email verification status, account creation date
- **BabyProfile**: Baby's nickname, date of birth (for age calculation), feeding style preference, daily meal target, allergies list, avoid list, dietary preferences, cultural preferences, practical constraints (prep time, batch days, staples). One profile per account in v1
- **FoodItem**: Name, category, allergen tags (e.g., dairy, egg, peanut, tree nut, wheat, soy, fish, shellfish), texture suitability levels, age suitability, safety notes, choking hazard flag
- **Recipe**: AI-generated at plan creation time. Contains name, ingredient list (with quantities), preparation steps, texture level, total prep time, allergen tags (derived from ingredients), age suitability, safe preparation notes for hazardous ingredients. Generated recipes are validated against safety rules before display
- **MealPlan**: Associated baby profile, date range, plan style, list of day entries. Each day contains meal slots with recipe references, "new food" flags, and notes. All plans retained indefinitely and accessible via history view; deletion only via baby profile deletion
- **MealLog**: Associated meal plan entry, date/time, outcome (ate/partial/refused), notes, baby profile reference
- **ReactionLog**: Timestamp, symptoms description, suspected foods (references to FoodItems), baby profile reference

## Clarifications

### Session 2026-01-12

- Q: Is the recipe/food database pre-populated, AI-generated, or user-created? → A: AI-generated recipes at plan creation time (LLM-based)
- Q: What is the acceptable wait time for generating a new meal plan? → A: Up to 30 seconds with progress indicator
- Q: How should the system handle AI generation failures? → A: Retry once automatically, then show error with "try again" option
- Q: What format(s) should shopping list export support? → A: Display in-app + share via native share sheet (copy/email/messaging)
- Q: How long should historical meal plans and logs be retained? → A: Keep all plans indefinitely, accessible in history view

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can sign up/login and reach baby profile creation screen in under 1 minute
- **SC-002**: Users can complete onboarding and generate their first 7-day plan in under 3 minutes
- **SC-003**: 100% of displayed plans pass safety validation (no blocked items, all hazards have safe-form guidance)
- **SC-004**: Users can generate and view a shopping list in 1 click from the plan view
- **SC-005**: Users can log a meal outcome in under 15 seconds from tapping "Log" to confirmation
- **SC-006**: When regenerating plans, system demonstrably incorporates avoid list and adapts to logged likes/refuses
- **SC-007**: All logged-in pages load and become interactive within 3 seconds on standard connections
- **SC-007a**: Meal plan generation completes within 30 seconds; user sees progress indicator during generation
- **SC-008**: Users can complete password reset flow within 2 minutes of initiating request
- **SC-009**: System correctly blocks all safety-restricted items (verified against CDC guidance list) with zero exceptions
- **SC-010**: 90% of users successfully complete first meal log within their first session
