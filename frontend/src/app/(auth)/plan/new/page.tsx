'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { api } from '@/lib/api'
import { MealFrequencyGuidance } from '@/components/plan/MealFrequencyGuidance'
import { PlanGenerationProgress } from '@/components/plan/PlanGenerationProgress'

export default function NewPlanPage() {
  const router = useRouter()
  const [numDays, setNumDays] = useState<3 | 7>(7)
  const [planStyle, setPlanStyle] = useState<'variety' | 'simple_repeats'>('variety')
  const [introduceNewFoods, setIntroduceNewFoods] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [planId, setPlanId] = useState<string | null>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setGenerating(true)

    try {
      const plan = await api.post<{ id: string }>('/plans', {
        num_days: numDays,
        plan_style: planStyle,
        introduce_new_foods: introduceNewFoods,
      })
      setPlanId(plan.id)
      // Redirect to plan view
      router.push(`/plan/${plan.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate plan')
      setGenerating(false)
    }
  }

  if (generating && !planId) {
    return <PlanGenerationProgress />
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="mx-auto max-w-2xl">
        <h1 className="mb-8 text-3xl font-bold text-gray-900">Generate Meal Plan</h1>

        <div className="mb-6 rounded-lg bg-white p-6 shadow-sm">
          <MealFrequencyGuidance />
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 rounded-lg bg-white p-8 shadow-sm">
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div>
            <label htmlFor="numDays" className="block text-sm font-medium text-gray-700">
              Plan Duration *
            </label>
            <select
              id="numDays"
              required
              value={numDays}
              onChange={(e) => setNumDays(parseInt(e.target.value) as 3 | 7)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            >
              <option value={3}>3 days</option>
              <option value={7}>7 days</option>
            </select>
          </div>

          <div>
            <label htmlFor="planStyle" className="block text-sm font-medium text-gray-700">
              Plan Style *
            </label>
            <select
              id="planStyle"
              required
              value={planStyle}
              onChange={(e) =>
                setPlanStyle(e.target.value as 'variety' | 'simple_repeats')
              }
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            >
              <option value="variety">More Variety</option>
              <option value="simple_repeats">Simple Repeats</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {planStyle === 'variety'
                ? 'Different meals each day'
                : 'Repeat familiar meals throughout the week'}
            </p>
          </div>

          <div className="flex items-center">
            <input
              id="introduceNewFoods"
              type="checkbox"
              checked={introduceNewFoods}
              onChange={(e) => setIntroduceNewFoods(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="introduceNewFoods" className="ml-2 block text-sm text-gray-700">
              Introduce new foods
            </label>
          </div>
          <p className="text-xs text-gray-500">
            Include 1-2 new foods per day to expand your baby's palate
          </p>

          <div>
            <button
              type="submit"
              disabled={generating}
              className="w-full rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {generating ? 'Generating Plan...' : 'Generate Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

