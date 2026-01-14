'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { IntroducedFoodCard } from '@/components/history/IntroducedFoodCard'
import { FoodDetailModal } from '@/components/history/FoodDetailModal'

interface IntroducedFood {
  food_item_id: string
  name: string
  category: string
  first_introduced: string | null
  ate_count: number
  partial_count: number
  refused_count: number
  preference_ratio: number
  has_reaction: boolean
}

type SortOption = 'date_introduced' | 'name' | 'preference_ratio'

export default function FoodHistoryPage() {
  const [foods, setFoods] = useState<IntroducedFood[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('date_introduced')
  const [selectedFood, setSelectedFood] = useState<IntroducedFood | null>(null)

  const loadFoods = async () => {
    try {
      setLoading(true)
      const data = await api.get<IntroducedFood[]>('/logs/foods/introduced', {
        params: { sort_by: sortBy },
      })
      setFoods(data)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load food history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFoods()
  }, [sortBy])

  // Group foods by category
  const groupedFoods = foods.reduce(
    (acc, food) => {
      const category = food.category || 'Other'
      if (!acc[category]) {
        acc[category] = []
      }
      acc[category].push(food)
      return acc
    },
    {} as Record<string, IntroducedFood[]>
  )

  // Summary stats
  const totalFoods = foods.length
  const favoriteFoods = foods.filter((f) => f.preference_ratio >= 0.7).length
  const reactionFoods = foods.filter((f) => f.has_reaction).length

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-white to-emerald-50">
        <div className="text-center">
          <div className="mb-4 inline-block h-10 w-10 animate-spin rounded-full border-4 border-emerald-600 border-t-transparent"></div>
          <p className="text-slate-600">Loading food history...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50 pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-slate-100 bg-white/80 px-4 py-4 backdrop-blur-lg">
        <div className="mx-auto max-w-2xl">
          <h1 className="text-xl font-bold text-slate-900">Food History</h1>
          <p className="text-sm text-slate-500">Track introduced foods and preferences</p>
        </div>
      </header>

      <main className="mx-auto max-w-2xl px-4 pt-6">
        {error && (
          <div className="mb-6 rounded-lg bg-rose-50 p-4 text-rose-700">
            {error}
          </div>
        )}

        {/* Summary stats */}
        {foods.length > 0 && (
          <div className="mb-6 grid grid-cols-3 gap-3">
            <div className="rounded-xl bg-white p-4 text-center shadow-sm">
              <span className="block text-2xl font-bold text-slate-900">
                {totalFoods}
              </span>
              <span className="text-sm text-slate-500">Foods tried</span>
            </div>
            <div className="rounded-xl bg-emerald-50 p-4 text-center shadow-sm">
              <span className="block text-2xl font-bold text-emerald-600">
                {favoriteFoods}
              </span>
              <span className="text-sm text-emerald-700">Favorites</span>
            </div>
            <div className="rounded-xl bg-rose-50 p-4 text-center shadow-sm">
              <span className="block text-2xl font-bold text-rose-600">
                {reactionFoods}
              </span>
              <span className="text-sm text-rose-700">Reactions</span>
            </div>
          </div>
        )}

        {/* Sort controls */}
        {foods.length > 0 && (
          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Sort by
            </label>
            <div className="flex gap-2">
              {[
                { value: 'date_introduced', label: 'Recent' },
                { value: 'name', label: 'Name' },
                { value: 'preference_ratio', label: 'Preference' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setSortBy(option.value as SortOption)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                    sortBy === option.value
                      ? 'bg-emerald-600 text-white'
                      : 'bg-white text-slate-600 shadow-sm hover:bg-slate-50'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Food list */}
        {foods.length > 0 ? (
          <div className="space-y-8">
            {sortBy === 'name' ? (
              // Show alphabetically without category grouping
              <div className="grid gap-3">
                {foods.map((food) => (
                  <IntroducedFoodCard
                    key={food.food_item_id}
                    name={food.name}
                    category={food.category}
                    firstIntroduced={food.first_introduced}
                    ateCount={food.ate_count}
                    partialCount={food.partial_count}
                    refusedCount={food.refused_count}
                    preferenceRatio={food.preference_ratio}
                    hasReaction={food.has_reaction}
                    onClick={() => setSelectedFood(food)}
                  />
                ))}
              </div>
            ) : (
              // Show with category grouping
              Object.entries(groupedFoods).map(([category, categoryFoods]) => (
                <div key={category}>
                  <h2 className="mb-3 text-sm font-semibold uppercase text-slate-500">
                    {category}
                  </h2>
                  <div className="grid gap-3">
                    {categoryFoods.map((food) => (
                      <IntroducedFoodCard
                        key={food.food_item_id}
                        name={food.name}
                        category={food.category}
                        firstIntroduced={food.first_introduced}
                        ateCount={food.ate_count}
                        partialCount={food.partial_count}
                        refusedCount={food.refused_count}
                        preferenceRatio={food.preference_ratio}
                        hasReaction={food.has_reaction}
                        onClick={() => setSelectedFood(food)}
                      />
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
            <div className="mb-4 text-4xl">🥗</div>
            <p className="mb-2 font-medium text-slate-700">No foods tracked yet</p>
            <p className="mb-4 text-sm text-slate-500">
              Log some meals to see your baby&apos;s food preferences
            </p>
            <Link
              href="/today"
              className="inline-block rounded-lg bg-emerald-600 px-6 py-2.5 font-medium text-white transition-colors hover:bg-emerald-700"
            >
              Log Today&apos;s Meals
            </Link>
          </div>
        )}

        {/* Navigation */}
        <div className="mt-8 flex gap-3">
          <Link
            href="/today"
            className="flex-1 rounded-xl border border-slate-200 bg-white py-3 text-center font-medium text-slate-600 shadow-sm transition-all hover:border-slate-300 hover:shadow"
          >
            Today
          </Link>
          <Link
            href="/history/reactions"
            className="flex-1 rounded-xl border border-slate-200 bg-white py-3 text-center font-medium text-slate-600 shadow-sm transition-all hover:border-slate-300 hover:shadow"
          >
            Reactions
          </Link>
        </div>
      </main>

      {/* Detail modal */}
      <FoodDetailModal
        isOpen={!!selectedFood}
        onClose={() => setSelectedFood(null)}
        food={
          selectedFood
            ? {
                name: selectedFood.name,
                category: selectedFood.category,
                firstIntroduced: selectedFood.first_introduced,
                ateCount: selectedFood.ate_count,
                partialCount: selectedFood.partial_count,
                refusedCount: selectedFood.refused_count,
                preferenceRatio: selectedFood.preference_ratio,
                hasReaction: selectedFood.has_reaction,
              }
            : null
        }
      />
    </div>
  )
}


