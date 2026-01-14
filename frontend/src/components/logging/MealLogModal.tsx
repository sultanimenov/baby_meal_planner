'use client'

import { useState } from 'react'
import type { MealOutcome, MealSlotType } from '@/lib/schemas'

interface MealLogModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: {
    outcome: MealOutcome
    notes?: string
    meal_slot?: MealSlotType
  }) => Promise<void>
  recipeTitle?: string
  mealSlot?: string
  showSlotSelector?: boolean
}

export function MealLogModal({
  isOpen,
  onClose,
  onSubmit,
  recipeTitle,
  mealSlot,
  showSlotSelector = false,
}: MealLogModalProps) {
  const [outcome, setOutcome] = useState<MealOutcome | null>(null)
  const [notes, setNotes] = useState('')
  const [selectedSlot, setSelectedSlot] = useState<MealSlotType | ''>('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleSubmit = async () => {
    if (!outcome) {
      setError('Please select an outcome')
      return
    }
    if (showSlotSelector && !selectedSlot) {
      setError('Please select a meal slot')
      return
    }

    setIsSubmitting(true)
    setError('')

    try {
      await onSubmit({
        outcome,
        notes: notes || undefined,
        meal_slot: showSlotSelector ? (selectedSlot as MealSlotType) : undefined,
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log meal')
    } finally {
      setIsSubmitting(false)
    }
  }

  const slotLabels: Record<string, string> = {
    breakfast: 'Breakfast',
    lunch: 'Lunch',
    dinner: 'Dinner',
    snack: 'Snack',
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 mx-4 w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="mb-2 text-xl font-bold text-slate-900">Log Meal</h2>
        {recipeTitle && (
          <p className="mb-4 text-slate-600">{recipeTitle}</p>
        )}
        {mealSlot && !showSlotSelector && (
          <p className="mb-4 text-sm text-slate-500">
            {slotLabels[mealSlot] || mealSlot}
          </p>
        )}

        {/* Slot selector */}
        {showSlotSelector && (
          <div className="mb-4">
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Meal Slot
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(['breakfast', 'lunch', 'dinner', 'snack'] as const).map((slot) => (
                <button
                  key={slot}
                  onClick={() => setSelectedSlot(slot)}
                  className={`rounded-lg border-2 py-2 text-sm font-medium transition-all ${
                    selectedSlot === slot
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}
                >
                  {slotLabels[slot]}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Outcome buttons */}
        <div className="mb-4">
          <label className="mb-2 block text-sm font-medium text-slate-700">
            How did it go?
          </label>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => setOutcome('ate')}
              className={`rounded-xl border-2 py-4 transition-all ${
                outcome === 'ate'
                  ? 'border-emerald-500 bg-emerald-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <span className="block text-2xl">✓</span>
              <span
                className={`text-sm font-medium ${
                  outcome === 'ate' ? 'text-emerald-700' : 'text-slate-600'
                }`}
              >
                Ate
              </span>
            </button>
            <button
              onClick={() => setOutcome('partial')}
              className={`rounded-xl border-2 py-4 transition-all ${
                outcome === 'partial'
                  ? 'border-amber-500 bg-amber-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <span className="block text-2xl">½</span>
              <span
                className={`text-sm font-medium ${
                  outcome === 'partial' ? 'text-amber-700' : 'text-slate-600'
                }`}
              >
                Partial
              </span>
            </button>
            <button
              onClick={() => setOutcome('refused')}
              className={`rounded-xl border-2 py-4 transition-all ${
                outcome === 'refused'
                  ? 'border-rose-500 bg-rose-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <span className="block text-2xl">✗</span>
              <span
                className={`text-sm font-medium ${
                  outcome === 'refused' ? 'text-rose-700' : 'text-slate-600'
                }`}
              >
                Refused
              </span>
            </button>
          </div>
        </div>

        {/* Notes */}
        <div className="mb-4">
          <label className="mb-2 block text-sm font-medium text-slate-700">
            Notes (optional)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any observations, reactions, or comments..."
            className="w-full resize-none rounded-lg border border-slate-200 p-3 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
            rows={3}
          />
        </div>

        {/* Error message */}
        {error && (
          <p className="mb-4 text-sm text-rose-600">{error}</p>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 rounded-lg border border-slate-200 py-3 font-medium text-slate-600 transition-colors hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !outcome}
            className="flex-1 rounded-lg bg-blue-600 py-3 font-medium text-white transition-colors hover:bg-blue-700 disabled:bg-slate-300"
          >
            {isSubmitting ? (
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
            ) : (
              'Save Log'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}


