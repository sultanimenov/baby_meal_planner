'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { TodayMealCard } from '@/components/logging/TodayMealCard'
import type { TodayMealSlot, MealOutcome, MealLogCreate } from '@/lib/schemas'

export default function TodayPage() {
  const [meals, setMeals] = useState<TodayMealSlot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedDate, setSelectedDate] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })

  const loadMeals = useCallback(async () => {
    try {
      setLoading(true)
      const data = await api.get<TodayMealSlot[]>('/logs/today', {
        params: { for_date: selectedDate },
      })
      setMeals(data)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load meals')
    } finally {
      setLoading(false)
    }
  }, [selectedDate])

  useEffect(() => {
    loadMeals()
  }, [loadMeals])

  const handleLogMeal = async (
    mealSlot: TodayMealSlot,
    outcome: MealOutcome,
    notes?: string
  ) => {
    const logData: MealLogCreate = {
      date: mealSlot.date,
      meal_slot: mealSlot.meal_slot,
      outcome,
      notes: notes || null,
      recipe_id: mealSlot.recipe_id || null,
      meal_plan_id: mealSlot.meal_plan_id || null,
    }

    await api.post('/logs/meal', logData)
    // Reload to get updated status
    await loadMeals()
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00')
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const dateOnly = new Date(date)
    dateOnly.setHours(0, 0, 0, 0)

    if (dateOnly.getTime() === today.getTime()) {
      return 'Today'
    }

    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    if (dateOnly.getTime() === yesterday.getTime()) {
      return 'Yesterday'
    }

    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
    })
  }

  const navigateDate = (direction: 'prev' | 'next') => {
    const current = new Date(selectedDate + 'T00:00:00')
    if (direction === 'prev') {
      current.setDate(current.getDate() - 1)
    } else {
      current.setDate(current.getDate() + 1)
    }
    setSelectedDate(current.toISOString().split('T')[0])
  }

  const isToday = selectedDate === new Date().toISOString().split('T')[0]

  // Calculate progress
  const totalMeals = meals.length
  const loggedMeals = meals.filter((m) => m.log).length
  const progressPercent = totalMeals > 0 ? (loggedMeals / totalMeals) * 100 : 0

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50">
        <div className="text-center">
          <div className="mb-4 inline-block h-10 w-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="text-slate-600">Loading meals...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-slate-100 bg-white/80 px-4 py-4 backdrop-blur-lg">
        <div className="mx-auto max-w-lg">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigateDate('prev')}
              className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
              aria-label="Previous day"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>

            <div className="text-center">
              <h1 className="text-xl font-bold text-slate-900">
                {formatDate(selectedDate)}
              </h1>
              {isToday && (
                <p className="text-sm text-slate-500">{getGreeting()}! 👋</p>
              )}
            </div>

            <button
              onClick={() => navigateDate('next')}
              className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
              aria-label="Next day"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-lg px-4 pt-6">
        {error && (
          <div className="mb-6 rounded-lg bg-rose-50 p-4 text-rose-700">
            {error}
          </div>
        )}

        {/* Progress indicator */}
        {totalMeals > 0 && (
          <div className="mb-6">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-slate-600">
                {loggedMeals} of {totalMeals} meals logged
              </span>
              {loggedMeals === totalMeals && (
                <span className="font-medium text-emerald-600">All done! 🎉</span>
              )}
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-500 to-emerald-500 transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        )}

        {/* Meal cards */}
        {meals.length > 0 ? (
          <div className="space-y-4">
            {meals.map((meal) => (
              <TodayMealCard
                key={`${meal.date}-${meal.meal_slot}`}
                mealSlot={meal}
                onLog={(outcome, notes) => handleLogMeal(meal, outcome, notes)}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
            <p className="mb-4 text-slate-600">No meals planned for this day</p>
            <Link
              href="/plan/new"
              className="inline-block rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white transition-colors hover:bg-blue-700"
            >
              Create a Meal Plan
            </Link>
          </div>
        )}

        {/* Quick actions */}
        <div className="mt-8 flex gap-3">
          <Link
            href="/plan/new"
            className="flex-1 rounded-xl border border-slate-200 bg-white py-3 text-center font-medium text-slate-600 shadow-sm transition-all hover:border-slate-300 hover:shadow"
          >
            New Plan
          </Link>
          <Link
            href="/"
            className="flex-1 rounded-xl border border-slate-200 bg-white py-3 text-center font-medium text-slate-600 shadow-sm transition-all hover:border-slate-300 hover:shadow"
          >
            View Plans
          </Link>
        </div>
      </main>
    </div>
  )
}


