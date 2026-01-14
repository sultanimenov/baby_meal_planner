'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

interface FoodItem {
  id: string
  name: string
  category: string
}

interface FoodSelectorProps {
  selectedFoodIds: string[]
  onChange: (foodIds: string[]) => void
  label?: string
}

export function FoodSelector({
  selectedFoodIds,
  onChange,
  label = 'Select Foods',
}: FoodSelectorProps) {
  const [foods, setFoods] = useState<FoodItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadFoods()
  }, [])

  const loadFoods = async () => {
    try {
      // For now, use recipes endpoint to get food data
      // In a full implementation, there would be a /foods endpoint
      const recipes = await api.get<any[]>('/recipes')
      // Extract unique foods from recipes
      const foodSet = new Map<string, FoodItem>()
      recipes.forEach((recipe) => {
        recipe.ingredients?.forEach((ing: any) => {
          if (ing.food_item_id && !foodSet.has(ing.food_item_id)) {
            foodSet.set(ing.food_item_id, {
              id: ing.food_item_id,
              name: ing.name || 'Unknown',
              category: ing.category || 'Other',
            })
          }
        })
      })
      setFoods(Array.from(foodSet.values()))
    } catch (err) {
      console.error('Failed to load foods:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleFood = (foodId: string) => {
    if (selectedFoodIds.includes(foodId)) {
      onChange(selectedFoodIds.filter((id) => id !== foodId))
    } else {
      onChange([...selectedFoodIds, foodId])
    }
  }

  const filteredFoods = foods.filter((food) =>
    food.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const groupedFoods = filteredFoods.reduce(
    (acc, food) => {
      const category = food.category || 'Other'
      if (!acc[category]) {
        acc[category] = []
      }
      acc[category].push(food)
      return acc
    },
    {} as Record<string, FoodItem[]>
  )

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-200 p-4">
        <p className="text-sm text-slate-500">Loading foods...</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-slate-700">{label}</label>

      {/* Search */}
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search foods..."
        className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
      />

      {/* Selected foods */}
      {selectedFoodIds.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedFoodIds.map((id) => {
            const food = foods.find((f) => f.id === id)
            return (
              <span
                key={id}
                className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700"
              >
                {food?.name || id}
                <button
                  onClick={() => toggleFood(id)}
                  className="ml-1 rounded-full p-0.5 hover:bg-blue-200"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-3 w-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </span>
            )
          })}
        </div>
      )}

      {/* Food list */}
      <div className="max-h-64 overflow-y-auto rounded-lg border border-slate-200">
        {Object.entries(groupedFoods).map(([category, categoryFoods]) => (
          <div key={category}>
            <div className="sticky top-0 bg-slate-50 px-3 py-1.5 text-xs font-semibold uppercase text-slate-500">
              {category}
            </div>
            {categoryFoods.map((food) => (
              <button
                key={food.id}
                onClick={() => toggleFood(food.id)}
                className={`flex w-full items-center justify-between px-3 py-2 text-left text-sm transition-colors hover:bg-slate-50 ${
                  selectedFoodIds.includes(food.id) ? 'bg-blue-50' : ''
                }`}
              >
                <span>{food.name}</span>
                {selectedFoodIds.includes(food.id) && (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </button>
            ))}
          </div>
        ))}
        {filteredFoods.length === 0 && (
          <p className="p-4 text-center text-sm text-slate-500">
            No foods found
          </p>
        )}
      </div>
    </div>
  )
}


