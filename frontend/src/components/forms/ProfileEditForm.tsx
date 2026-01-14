'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import type { BabyProfile } from '@/lib/schemas'

interface ProfileEditFormProps {
  profile: BabyProfile
  onSuccess?: () => void
  onCancel?: () => void
}

export function ProfileEditForm({
  profile,
  onSuccess,
  onCancel,
}: ProfileEditFormProps) {
  const [nickname, setNickname] = useState(profile.nickname)
  const [feedingStyle, setFeedingStyle] = useState(profile.feeding_style)
  const [mealsPerDay, setMealsPerDay] = useState(profile.meals_per_day)
  const [dietaryPreference, setDietaryPreference] = useState(
    profile.dietary_preference
  )
  const [maxPrepMinutes, setMaxPrepMinutes] = useState(profile.max_prep_minutes)
  const [allergens, setAllergens] = useState(profile.allergens.join(', '))
  const [avoidList, setAvoidList] = useState(profile.avoid_list.join(', '))
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const commonAllergens = [
    'dairy',
    'egg',
    'peanut',
    'tree_nut',
    'wheat',
    'soy',
    'fish',
    'shellfish',
    'sesame',
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')

    try {
      await api.put('/baby-profile/me', {
        nickname,
        feeding_style: feedingStyle,
        meals_per_day: mealsPerDay,
        dietary_preference: dietaryPreference,
        max_prep_minutes: maxPrepMinutes,
        allergens: allergens
          .split(',')
          .map((a) => a.trim())
          .filter(Boolean),
        avoid_list: avoidList
          .split(',')
          .map((a) => a.trim())
          .filter(Boolean),
      })
      onSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
    } finally {
      setIsSubmitting(false)
    }
  }

  const toggleAllergen = (allergen: string) => {
    const current = allergens
      .split(',')
      .map((a) => a.trim())
      .filter(Boolean)

    if (current.includes(allergen)) {
      setAllergens(current.filter((a) => a !== allergen).join(', '))
    } else {
      setAllergens([...current, allergen].join(', '))
    }
  }

  const currentAllergens = allergens
    .split(',')
    .map((a) => a.trim())
    .filter(Boolean)

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Nickname */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Baby&apos;s Nickname
        </label>
        <input
          type="text"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          className="w-full rounded-lg border border-slate-200 px-3 py-2.5 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          required
        />
      </div>

      {/* Feeding Style */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Feeding Style
        </label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { value: 'puree', label: 'Purées', emoji: '🥣' },
            { value: 'blw', label: 'Baby-Led', emoji: '🖐️' },
            { value: 'mixed', label: 'Mixed', emoji: '🍽️' },
          ].map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setFeedingStyle(option.value as any)}
              className={`rounded-lg border-2 p-3 text-center transition-all ${
                feedingStyle === option.value
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <span className="block text-xl">{option.emoji}</span>
              <span
                className={`text-sm font-medium ${
                  feedingStyle === option.value
                    ? 'text-blue-700'
                    : 'text-slate-600'
                }`}
              >
                {option.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Meals Per Day */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Meals Per Day
        </label>
        <div className="flex gap-2">
          {[1, 2, 3].map((num) => (
            <button
              key={num}
              type="button"
              onClick={() => setMealsPerDay(num)}
              className={`flex-1 rounded-lg border-2 py-2.5 text-center font-medium transition-all ${
                mealsPerDay === num
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-slate-200 text-slate-600 hover:border-slate-300'
              }`}
            >
              {num} {num === 1 ? 'meal' : 'meals'}
            </button>
          ))}
        </div>
      </div>

      {/* Dietary Preference */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Dietary Preference
        </label>
        <div className="grid grid-cols-2 gap-2">
          {[
            { value: 'omnivore', label: 'Omnivore' },
            { value: 'vegetarian', label: 'Vegetarian' },
          ].map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setDietaryPreference(option.value as any)}
              className={`rounded-lg border-2 py-2.5 text-center font-medium transition-all ${
                dietaryPreference === option.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-slate-200 text-slate-600 hover:border-slate-300'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Max Prep Time */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Max Prep Time: {maxPrepMinutes} minutes
        </label>
        <input
          type="range"
          min="5"
          max="60"
          step="5"
          value={maxPrepMinutes}
          onChange={(e) => setMaxPrepMinutes(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-slate-500">
          <span>5 min</span>
          <span>60 min</span>
        </div>
      </div>

      {/* Allergens */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Known Allergens
        </label>
        <div className="mb-2 flex flex-wrap gap-2">
          {commonAllergens.map((allergen) => (
            <button
              key={allergen}
              type="button"
              onClick={() => toggleAllergen(allergen)}
              className={`rounded-full px-3 py-1 text-sm capitalize transition-all ${
                currentAllergens.includes(allergen)
                  ? 'bg-rose-100 text-rose-700'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {allergen.replace('_', ' ')}
            </button>
          ))}
        </div>
        <input
          type="text"
          value={allergens}
          onChange={(e) => setAllergens(e.target.value)}
          placeholder="Other allergens (comma-separated)"
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
      </div>

      {/* Avoid List */}
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Foods to Avoid
        </label>
        <input
          type="text"
          value={avoidList}
          onChange={(e) => setAvoidList(e.target.value)}
          placeholder="Foods to avoid (comma-separated)"
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
        <p className="mt-1 text-xs text-slate-500">
          Foods here will never appear in meal plans
        </p>
      </div>

      {/* Error */}
      {error && <p className="text-sm text-rose-600">{error}</p>}

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
          className="flex-1 rounded-lg bg-blue-600 py-3 font-medium text-white transition-colors hover:bg-blue-700 disabled:bg-slate-300"
        >
          {isSubmitting ? (
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
          ) : (
            'Save Changes'
          )}
        </button>
      </div>
    </form>
  )
}


