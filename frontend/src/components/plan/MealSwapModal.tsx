'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { Recipe } from '@/lib/schemas'

interface MealSwapModalProps {
  isOpen: boolean
  onClose: () => void
  onSwap: (recipeId: string) => Promise<void>
  currentRecipeId?: string
  dayDate: string
  mealSlot: string
  planId: string
}

export function MealSwapModal({
  isOpen,
  onClose,
  onSwap,
  currentRecipeId,
  dayDate,
  mealSlot,
  planId,
}: MealSwapModalProps) {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedRecipeId, setSelectedRecipeId] = useState<string>('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadRecipes()
    }
  }, [isOpen])

  const loadRecipes = async () => {
    try {
      setLoading(true)
      // In a real app, this would filter by baby's age/preferences
      const recipesData = await api.get<Recipe[]>('/recipes')
      setRecipes(recipesData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recipes')
    } finally {
      setLoading(false)
    }
  }

  const handleSwap = async () => {
    if (!selectedRecipeId) {
      setError('Please select a recipe')
      return
    }

    try {
      await onSwap(selectedRecipeId)
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to swap meal')
    }
  }

  if (!isOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Swap Meal</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600">
            Replace meal for {dayDate} - {mealSlot}
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="py-8 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
            <p className="mt-2 text-sm text-gray-600">Loading recipes...</p>
          </div>
        ) : (
          <div className="mb-4 max-h-64 space-y-2 overflow-y-auto">
            {recipes.map((recipe) => (
              <label
                key={recipe.id}
                className={`flex cursor-pointer items-center rounded border p-3 hover:bg-gray-50 ${
                  selectedRecipeId === recipe.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
              >
                <input
                  type="radio"
                  name="recipe"
                  value={recipe.id}
                  checked={selectedRecipeId === recipe.id}
                  onChange={(e) => setSelectedRecipeId(e.target.value)}
                  className="mr-3"
                />
                <div>
                  <p className="font-medium">{recipe.title}</p>
                  <p className="text-xs text-gray-600">
                    {recipe.texture_level} • {recipe.estimated_prep_minutes} min
                  </p>
                </div>
              </label>
            ))}
          </div>
        )}

        <div className="flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSwap}
            disabled={!selectedRecipeId || loading}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Swap Meal
          </button>
        </div>
      </div>
    </div>
  )
}


