'use client'

import { useState } from 'react'
import type { TodayMealSlot, MealOutcome } from '@/lib/schemas'

interface TodayMealCardProps {
  mealSlot: TodayMealSlot
  onLog: (outcome: MealOutcome, notes?: string) => Promise<void>
}

export function TodayMealCard({ mealSlot, onLog }: TodayMealCardProps) {
  const [showNotes, setShowNotes] = useState(false)
  const [notes, setNotes] = useState('')
  const [isLogging, setIsLogging] = useState(false)
  const [selectedOutcome, setSelectedOutcome] = useState<MealOutcome | null>(null)

  const slotLabels: Record<string, string> = {
    breakfast: '🌅 Breakfast',
    lunch: '☀️ Lunch',
    dinner: '🌙 Dinner',
    snack: '🍎 Snack',
  }

  const outcomeStyles: Record<MealOutcome, { bg: string; text: string; icon: string }> = {
    ate: { bg: 'bg-emerald-100', text: 'text-emerald-700', icon: '✓' },
    partial: { bg: 'bg-amber-100', text: 'text-amber-700', icon: '½' },
    refused: { bg: 'bg-rose-100', text: 'text-rose-700', icon: '✗' },
  }

  const handleQuickLog = async (outcome: MealOutcome) => {
    setSelectedOutcome(outcome)
    setIsLogging(true)
    try {
      await onLog(outcome)
    } finally {
      setIsLogging(false)
      setSelectedOutcome(null)
    }
  }

  const handleLogWithNotes = async (outcome: MealOutcome) => {
    setSelectedOutcome(outcome)
    setIsLogging(true)
    try {
      await onLog(outcome, notes)
      setShowNotes(false)
      setNotes('')
    } finally {
      setIsLogging(false)
      setSelectedOutcome(null)
    }
  }

  const isLogged = !!mealSlot.log

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:shadow-md">
      {/* Header */}
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">
            {slotLabels[mealSlot.meal_slot] || mealSlot.meal_slot}
          </h3>
          {mealSlot.recipe_title && (
            <p className="mt-1 text-sm text-slate-600">{mealSlot.recipe_title}</p>
          )}
          {!mealSlot.recipe_title && !isLogged && (
            <p className="mt-1 text-sm text-slate-400 italic">No recipe planned</p>
          )}
        </div>

        {/* Status badge */}
        {isLogged && mealSlot.log && (
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium ${
              outcomeStyles[mealSlot.log.outcome].bg
            } ${outcomeStyles[mealSlot.log.outcome].text}`}
          >
            <span>{outcomeStyles[mealSlot.log.outcome].icon}</span>
            <span className="capitalize">{mealSlot.log.outcome}</span>
          </span>
        )}
      </div>

      {/* Logged notes */}
      {isLogged && mealSlot.log?.notes && (
        <div className="mb-4 rounded-lg bg-slate-50 p-3">
          <p className="text-sm text-slate-600">{mealSlot.log.notes}</p>
        </div>
      )}

      {/* Quick log buttons (when not logged) */}
      {!isLogged && !showNotes && (
        <div className="flex gap-2">
          <button
            onClick={() => handleQuickLog('ate')}
            disabled={isLogging}
            className="flex-1 rounded-xl bg-emerald-500 py-3 font-medium text-white transition-all hover:bg-emerald-600 active:scale-[0.98] disabled:opacity-50"
          >
            {isLogging && selectedOutcome === 'ate' ? (
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
            ) : (
              '✓ Ate'
            )}
          </button>
          <button
            onClick={() => handleQuickLog('partial')}
            disabled={isLogging}
            className="flex-1 rounded-xl bg-amber-500 py-3 font-medium text-white transition-all hover:bg-amber-600 active:scale-[0.98] disabled:opacity-50"
          >
            {isLogging && selectedOutcome === 'partial' ? (
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
            ) : (
              '½ Partial'
            )}
          </button>
          <button
            onClick={() => handleQuickLog('refused')}
            disabled={isLogging}
            className="flex-1 rounded-xl bg-rose-500 py-3 font-medium text-white transition-all hover:bg-rose-600 active:scale-[0.98] disabled:opacity-50"
          >
            {isLogging && selectedOutcome === 'refused' ? (
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
            ) : (
              '✗ Refused'
            )}
          </button>
        </div>
      )}

      {/* Add notes button */}
      {!isLogged && !showNotes && (
        <button
          onClick={() => setShowNotes(true)}
          className="mt-3 w-full rounded-lg border border-slate-200 py-2 text-sm text-slate-500 transition-colors hover:border-slate-300 hover:text-slate-700"
        >
          + Add notes
        </button>
      )}

      {/* Notes input area */}
      {!isLogged && showNotes && (
        <div className="space-y-3">
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="How did the meal go? Any observations..."
            className="w-full resize-none rounded-lg border border-slate-200 p-3 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
            rows={2}
          />
          <div className="flex gap-2">
            <button
              onClick={() => handleLogWithNotes('ate')}
              disabled={isLogging}
              className="flex-1 rounded-lg bg-emerald-500 py-2.5 text-sm font-medium text-white transition-all hover:bg-emerald-600 disabled:opacity-50"
            >
              ✓ Ate
            </button>
            <button
              onClick={() => handleLogWithNotes('partial')}
              disabled={isLogging}
              className="flex-1 rounded-lg bg-amber-500 py-2.5 text-sm font-medium text-white transition-all hover:bg-amber-600 disabled:opacity-50"
            >
              ½ Partial
            </button>
            <button
              onClick={() => handleLogWithNotes('refused')}
              disabled={isLogging}
              className="flex-1 rounded-lg bg-rose-500 py-2.5 text-sm font-medium text-white transition-all hover:bg-rose-600 disabled:opacity-50"
            >
              ✗ Refused
            </button>
          </div>
          <button
            onClick={() => {
              setShowNotes(false)
              setNotes('')
            }}
            className="w-full rounded-lg py-2 text-sm text-slate-500 hover:text-slate-700"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Update log button (when already logged) */}
      {isLogged && (
        <button
          onClick={() => setShowNotes(true)}
          className="mt-3 w-full rounded-lg border border-slate-200 py-2 text-sm text-slate-500 transition-colors hover:border-slate-300 hover:text-slate-700"
        >
          Update log
        </button>
      )}
    </div>
  )
}


