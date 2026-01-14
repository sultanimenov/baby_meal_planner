'use client'

import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { PlanDayCard } from '@/components/plan/PlanDayCard'
import { SafetyBadge } from '@/components/plan/SafetyBadge'
import { ShoppingList } from '@/components/plan/ShoppingList'
import { PrepSuggestions } from '@/components/plan/PrepSuggestions'
import { MealSwapModal } from '@/components/plan/MealSwapModal'
import type { MealPlan } from '@/lib/schemas'

export default function PlanViewPage() {
  const params = useParams()
  const planId = params.id as string
  const [plan, setPlan] = useState<MealPlan | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [swapModalOpen, setSwapModalOpen] = useState(false)
  const [swapContext, setSwapContext] = useState<{
    dayDate: string
    mealSlot: string
  } | null>(null)

  useEffect(() => {
    loadPlan()
  }, [planId])

  const loadPlan = async () => {
    try {
      const planData = await api.get<MealPlan>(`/plans/${planId}`)
      setPlan(planData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load plan')
    } finally {
      setLoading(false)
    }
  }

  const handleSwapMeal = async (recipeId: string) => {
    if (!swapContext || !plan) return

    try {
      await api.patch(`/plans/${planId}/swap-meal`, null, {
        params: {
          day_date: swapContext.dayDate,
          meal_slot: swapContext.mealSlot,
          new_recipe_id: recipeId,
        },
      })
      // Reload plan to get updated shopping list
      await loadPlan()
    } catch (err) {
      throw err
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="text-gray-600">Loading plan...</p>
        </div>
      </div>
    )
  }

  if (error || !plan) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error || 'Plan not found'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Meal Plan</h1>
            <p className="mt-1 text-gray-600">
              {plan.num_days}-day plan • {plan.plan_style === 'variety' ? 'More Variety' : 'Simple Repeats'}
            </p>
          </div>
          <SafetyBadge validated={true} />
        </div>

        <div className="space-y-6">
          {plan.days.map((day: any, idx: number) => (
            <PlanDayCard
              key={idx}
              date={day.date}
              meals={day.meals || []}
              onSwapMeal={(dayDate, mealSlot) => {
                setSwapContext({ dayDate, mealSlot })
                setSwapModalOpen(true)
              }}
            />
          ))}
        </div>

        {plan.shopping_list && Object.keys(plan.shopping_list).length > 0 && (
          <div className="mt-8">
            <ShoppingList shoppingList={plan.shopping_list as any} />
          </div>
        )}

        {plan.prep_suggestions && plan.prep_suggestions.length > 0 && (
          <div className="mt-6">
            <PrepSuggestions suggestions={plan.prep_suggestions as any} />
          </div>
        )}

        {swapModalOpen && swapContext && (
          <MealSwapModal
            isOpen={swapModalOpen}
            onClose={() => {
              setSwapModalOpen(false)
              setSwapContext(null)
            }}
            onSwap={handleSwapMeal}
            dayDate={swapContext.dayDate}
            mealSlot={swapContext.mealSlot}
            planId={planId}
          />
        )}
      </div>
    </div>
  )
}

