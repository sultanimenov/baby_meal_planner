'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import { FoodSelector } from './FoodSelector'

interface ReactionLogFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export function ReactionLogForm({ onSuccess, onCancel }: ReactionLogFormProps) {
  const [symptoms, setSymptoms] = useState('')
  const [severity, setSeverity] = useState<'mild' | 'moderate' | 'severe'>('mild')
  const [selectedFoodIds, setSelectedFoodIds] = useState<string[]>([])
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const severityOptions = [
    { value: 'mild', label: 'Mild', description: 'Minor symptoms, no medical attention needed', color: 'amber' },
    { value: 'moderate', label: 'Moderate', description: 'Noticeable symptoms, may need monitoring', color: 'orange' },
    { value: 'severe', label: 'Severe', description: 'Serious symptoms, seek medical attention', color: 'rose' },
  ] as const

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!symptoms.trim()) {
      setError('Please describe the symptoms')
      return
    }

    setIsSubmitting(true)
    setError('')

    try {
      await api.post('/logs/reaction', {
        symptoms: symptoms.trim(),
        severity,
        suspected_food_ids: selectedFoodIds,
        suspected_recipe_ids: [],
        notes: notes.trim() || null,
      })
      onSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log reaction')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Symptoms */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Symptoms <span className="text-rose-500">*</span>
        </label>
        <textarea
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          placeholder="Describe the symptoms you noticed (e.g., rash, hives, vomiting, diarrhea...)"
          className="w-full resize-none rounded-lg border border-slate-200 p-3 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          rows={3}
          required
        />
      </div>

      {/* Severity */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Severity
        </label>
        <div className="grid grid-cols-3 gap-2">
          {severityOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setSeverity(option.value)}
              className={`rounded-lg border-2 p-3 text-left transition-all ${
                severity === option.value
                  ? option.color === 'amber'
                    ? 'border-amber-500 bg-amber-50'
                    : option.color === 'orange'
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-rose-500 bg-rose-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <span
                className={`block font-medium ${
                  severity === option.value
                    ? option.color === 'amber'
                      ? 'text-amber-700'
                      : option.color === 'orange'
                        ? 'text-orange-700'
                        : 'text-rose-700'
                    : 'text-slate-700'
                }`}
              >
                {option.label}
              </span>
              <span className="mt-0.5 block text-xs text-slate-500">
                {option.description}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Suspected Foods */}
      <FoodSelector
        selectedFoodIds={selectedFoodIds}
        onChange={setSelectedFoodIds}
        label="Suspected Foods (optional)"
      />

      {/* Additional Notes */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Additional Notes
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any other relevant information (timing, duration, treatments tried...)"
          className="w-full resize-none rounded-lg border border-slate-200 p-3 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          rows={2}
        />
      </div>

      {/* Error */}
      {error && (
        <p className="text-sm text-rose-600">{error}</p>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 rounded-lg border border-slate-200 py-3 font-medium text-slate-600 transition-colors hover:bg-slate-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 rounded-lg bg-rose-600 py-3 font-medium text-white transition-colors hover:bg-rose-700 disabled:bg-slate-300"
        >
          {isSubmitting ? (
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
          ) : (
            'Log Reaction'
          )}
        </button>
      </div>
    </form>
  )
}


