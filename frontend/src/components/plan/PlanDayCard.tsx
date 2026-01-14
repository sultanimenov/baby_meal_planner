'use client'

import { MealCard } from './MealCard'

interface Meal {
  slot: string
  recipe_id?: string
  recipe_title?: string
  is_new_food?: boolean
  new_food_items?: string[]
  notes?: string
}

interface PlanDayCardProps {
  date: string
  meals: Meal[]
  onSwapMeal?: (dayDate: string, mealSlot: string) => void
}

export function PlanDayCard({ date, meals, onSwapMeal }: PlanDayCardProps) {
  const dateObj = new Date(date)
  const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' })
  const dateStr = dateObj.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-4 border-b border-gray-200 pb-2">
        <h3 className="text-lg font-semibold text-gray-900">{dayName}</h3>
        <p className="text-sm text-gray-600">{dateStr}</p>
      </div>

      <div className="space-y-3">
        {meals.map((meal, idx) => (
          <div key={idx} className="relative">
            <MealCard
              slot={meal.slot}
              recipeTitle={meal.recipe_title}
              recipeId={meal.recipe_id}
              isNewFood={meal.is_new_food}
              newFoodItems={meal.new_food_items}
              notes={meal.notes}
              safetyValidated={true}
            />
            {onSwapMeal && (
              <button
                onClick={() => onSwapMeal(date, meal.slot)}
                className="absolute right-2 top-2 rounded bg-gray-100 px-2 py-1 text-xs text-gray-600 hover:bg-gray-200"
              >
                Swap
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

