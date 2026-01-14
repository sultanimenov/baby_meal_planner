'use client'

import { SafetyBadge } from './SafetyBadge'

interface MealCardProps {
  slot: string
  recipeTitle?: string
  recipeId?: string
  isNewFood?: boolean
  newFoodItems?: string[]
  notes?: string
  safetyValidated?: boolean
}

export function MealCard({
  slot,
  recipeTitle,
  recipeId,
  isNewFood,
  newFoodItems = [],
  notes,
  safetyValidated = true,
}: MealCardProps) {
  const slotLabels: Record<string, string> = {
    breakfast: 'Breakfast',
    lunch: 'Lunch',
    dinner: 'Dinner',
    snack: 'Snack',
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-center justify-between">
        <h4 className="font-semibold text-gray-900">{slotLabels[slot] || slot}</h4>
        {safetyValidated && <SafetyBadge validated={true} />}
      </div>

      {recipeTitle && (
        <div className="mb-2">
          <p className="font-medium text-gray-800">{recipeTitle}</p>
          {isNewFood && (
            <span className="mt-1 inline-block rounded bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
              NEW FOOD
            </span>
          )}
        </div>
      )}

      {newFoodItems.length > 0 && (
        <div className="mb-2">
          <p className="text-xs font-medium text-gray-600">New foods:</p>
          <ul className="list-disc pl-5 text-xs text-gray-600">
            {newFoodItems.map((food, idx) => (
              <li key={idx}>{food}</li>
            ))}
          </ul>
        </div>
      )}

      {notes && (
        <p className="mt-2 text-sm text-gray-600">{notes}</p>
      )}

      {!recipeTitle && (
        <p className="text-sm text-gray-500">No recipe assigned</p>
      )}
    </div>
  )
}


