# Data Model: Infant Meal Planner

**Date**: 2026-01-12  
**ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐
│    User     │───1:1─│ BabyProfile  │
└─────────────┘       └──────────────┘
                            │
                            │ 1:N
                            ▼
                      ┌──────────────┐
                      │   MealPlan   │
                      └──────────────┘
                            │
                            │ 1:N
                            ▼
                      ┌──────────────┐
                      │   MealLog    │
                      └──────────────┘

┌─────────────┐       ┌──────────────┐
│  FoodItem   │◄──N:M─│    Recipe    │
└─────────────┘       └──────────────┘

┌──────────────┐
│ ReactionLog  │───N:1─► BabyProfile
└──────────────┘
```

## Entities

### User

Managed by fastapi-users. Extended fields as needed.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Lowercase, validated |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt hash |
| is_active | BOOLEAN | DEFAULT true | Account status |
| is_verified | BOOLEAN | DEFAULT false | Email verified |
| created_at | TIMESTAMP | NOT NULL | UTC |
| updated_at | TIMESTAMP | NOT NULL | UTC |

### BabyProfile

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| user_id | UUID | FK(users.id), UNIQUE | 1:1 for v1 |
| nickname | VARCHAR(100) | NOT NULL | Display name |
| date_of_birth | DATE | NOT NULL | For age calculation |
| feeding_style | VARCHAR(20) | NOT NULL | ENUM: puree, blw, mixed |
| meals_per_day | SMALLINT | NOT NULL, CHECK(1-3) | Target meals |
| dietary_preference | VARCHAR(20) | DEFAULT 'omnivore' | ENUM: vegetarian, omnivore |
| cuisine_preferences | JSONB | DEFAULT '[]' | Array of cuisine tags |
| allergens | JSONB | DEFAULT '[]' | Known allergens |
| avoid_list | JSONB | DEFAULT '[]' | Foods to avoid |
| max_prep_minutes | SMALLINT | DEFAULT 30 | Per meal constraint |
| batch_cook_days | JSONB | DEFAULT '[]' | Days for batch prep |
| pantry_staples | JSONB | DEFAULT '[]' | Common ingredients |
| created_at | TIMESTAMP | NOT NULL | UTC |
| updated_at | TIMESTAMP | NOT NULL | UTC |

**Computed Properties**:
- `age_in_months`: Calculated from date_of_birth at runtime

**Indexes**:
- UNIQUE(user_id) - One profile per user for v1

### FoodItem

Reference data for ingredients with safety metadata.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Canonical name |
| category | VARCHAR(50) | NOT NULL | produce, protein, grain, dairy, etc. |
| allergen_tags | JSONB | DEFAULT '[]' | dairy, egg, peanut, tree_nut, wheat, soy, fish, shellfish |
| texture_suitability | JSONB | DEFAULT '{}' | {puree: true, blw: false, mixed: true} |
| min_age_months | SMALLINT | DEFAULT 6 | Earliest introduction |
| is_choking_hazard | BOOLEAN | DEFAULT false | Requires safe-form guidance |
| safe_form_notes | TEXT | NULL | How to prepare safely |
| is_blocked_under_12m | BOOLEAN | DEFAULT false | e.g., honey |
| blocked_reason | TEXT | NULL | CDC/safety reference |
| created_at | TIMESTAMP | NOT NULL | UTC |

**Indexes**:
- INDEX(category)
- INDEX(is_blocked_under_12m)

### Recipe

Curated recipes with safety metadata (seeded, not user-created).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| title | VARCHAR(200) | NOT NULL | Recipe name |
| description | TEXT | NULL | Brief description |
| texture_level | VARCHAR(20) | NOT NULL | ENUM: puree, soft_mash, finger_food, mixed |
| ingredients | JSONB | NOT NULL | [{food_item_id, quantity, unit, prep_notes}] |
| steps | JSONB | NOT NULL | [{order, instruction}] |
| allergen_tags | JSONB | DEFAULT '[]' | Derived from ingredients |
| estimated_prep_minutes | SMALLINT | NOT NULL | Total prep time |
| servings | SMALLINT | DEFAULT 1 | Portion count |
| min_age_months | SMALLINT | DEFAULT 6 | Minimum age |
| tags | JSONB | DEFAULT '[]' | breakfast, lunch, dinner, snack, etc. |
| cuisine_tags | JSONB | DEFAULT '[]' | asian, mediterranean, etc. |
| is_vegetarian | BOOLEAN | DEFAULT false | No meat/fish |
| safety_notes | TEXT | NULL | Preparation safety tips |
| created_at | TIMESTAMP | NOT NULL | UTC |
| updated_at | TIMESTAMP | NOT NULL | UTC |

**Indexes**:
- INDEX(texture_level)
- INDEX(is_vegetarian)
- GIN INDEX(allergen_tags)
- GIN INDEX(tags)

### MealPlan

Generated meal plan with embedded day/meal structure.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| user_id | UUID | FK(users.id), NOT NULL | Owner |
| baby_profile_id | UUID | FK(baby_profiles.id), NOT NULL | Target baby |
| start_date | DATE | NOT NULL | Plan start |
| num_days | SMALLINT | NOT NULL | 3 or 7 |
| plan_style | VARCHAR(20) | NOT NULL | ENUM: variety, simple_repeats |
| introduce_new_foods | BOOLEAN | DEFAULT false | Include new foods flag |
| days | JSONB | NOT NULL | See Days Schema below |
| shopping_list | JSONB | DEFAULT '{}' | Aggregated ingredients |
| prep_suggestions | JSONB | DEFAULT '[]' | Batch cooking tips |
| schema_version | SMALLINT | DEFAULT 1 | For migrations |
| generation_metadata | JSONB | DEFAULT '{}' | LLM trace info |
| created_at | TIMESTAMP | NOT NULL | UTC |

**Days Schema** (JSONB):
```json
{
  "days": [
    {
      "date": "2026-01-12",
      "meals": [
        {
          "slot": "breakfast",
          "recipe_id": "uuid",
          "is_new_food": false,
          "new_food_items": [],
          "notes": "optional"
        }
      ]
    }
  ]
}
```

**Indexes**:
- INDEX(user_id, start_date)
- INDEX(baby_profile_id)

### MealLog

Log of meal outcomes for each meal slot.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| user_id | UUID | FK(users.id), NOT NULL | Logger |
| baby_profile_id | UUID | FK(baby_profiles.id), NOT NULL | Baby |
| meal_plan_id | UUID | FK(meal_plans.id), NULL | Optional plan link |
| date | DATE | NOT NULL | Meal date |
| meal_slot | VARCHAR(20) | NOT NULL | breakfast, lunch, dinner, snack |
| recipe_id | UUID | FK(recipes.id), NULL | If from plan |
| outcome | VARCHAR(20) | NOT NULL | ENUM: ate, partial, refused |
| notes | TEXT | NULL | Optional notes |
| created_at | TIMESTAMP | NOT NULL | UTC |

**Indexes**:
- INDEX(baby_profile_id, date)
- INDEX(recipe_id)

### ReactionLog

Log of suspected allergic or adverse reactions.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK | Auto-generated |
| user_id | UUID | FK(users.id), NOT NULL | Logger |
| baby_profile_id | UUID | FK(baby_profiles.id), NOT NULL | Baby |
| occurred_at | TIMESTAMP | NOT NULL | When reaction noticed |
| symptoms | TEXT | NOT NULL | Free-text description |
| severity | VARCHAR(20) | DEFAULT 'mild' | ENUM: mild, moderate, severe |
| suspected_food_ids | JSONB | DEFAULT '[]' | Array of food_item UUIDs |
| suspected_recipe_ids | JSONB | DEFAULT '[]' | Array of recipe UUIDs |
| notes | TEXT | NULL | Additional notes |
| created_at | TIMESTAMP | NOT NULL | UTC |

**Indexes**:
- INDEX(baby_profile_id, occurred_at)
- GIN INDEX(suspected_food_ids)

## Validation Rules

### BabyProfile
- `date_of_birth` must be within last 24 months
- `feeding_style` must be one of: puree, blw, mixed
- `meals_per_day` must be 1, 2, or 3
- `allergens` items must match known allergen tags

### Recipe
- `allergen_tags` must be derived from ingredients (computed on save)
- `min_age_months` must be >= 4 and <= 24
- `ingredients` must reference valid food_item_ids

### MealPlan
- `num_days` must be 3 or 7
- `days` array length must equal `num_days`
- All recipe_ids in days must reference valid recipes

### MealLog
- `outcome` must be one of: ate, partial, refused
- `date` cannot be in the future

## State Transitions

### MealPlan Lifecycle
```
[draft] → [validated] → [persisted]
   ↓          ↓
[failed]   [repair] → [validated]
```

No explicit status column; plan is only persisted after validation passes.

## Seed Data Requirements

### FoodItem Seeds (~100 items)
- Common infant-safe ingredients
- Pre-tagged with allergens
- Choking hazard flags set
- Honey marked as blocked_under_12m

### Recipe Seeds (~50 recipes)
- Mix of textures: puree, soft_mash, finger_food
- Variety of meal slots: breakfast, lunch, dinner, snack
- Vegetarian and omnivore options
- Range of prep times (5-30 minutes)
- Properly tagged with allergens and safety notes

