'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import type { BabyProfileCreate } from '@/lib/schemas'

interface BabyProfileFormProps {
  onSuccess?: () => void
}

export function BabyProfileForm({ onSuccess }: BabyProfileFormProps) {
  const [formData, setFormData] = useState<BabyProfileCreate>({
    nickname: '',
    date_of_birth: '',
    feeding_style: 'puree',
    meals_per_day: 2,
    dietary_preference: 'omnivore',
    cuisine_preferences: [],
    allergens: [],
    avoid_list: [],
    max_prep_minutes: 30,
    batch_cook_days: [],
    pantry_staples: [],
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await api.post('/baby-profile', formData)
      onSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div>
        <label htmlFor="nickname" className="block text-sm font-medium text-gray-700">
          Baby's Nickname *
        </label>
        <input
          id="nickname"
          type="text"
          required
          value={formData.nickname}
          onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700">
          Date of Birth *
        </label>
        <input
          id="date_of_birth"
          type="date"
          required
          value={formData.date_of_birth}
          onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="feeding_style" className="block text-sm font-medium text-gray-700">
          Feeding Style *
        </label>
        <select
          id="feeding_style"
          required
          value={formData.feeding_style}
          onChange={(e) =>
            setFormData({ ...formData, feeding_style: e.target.value as 'puree' | 'blw' | 'mixed' })
          }
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        >
          <option value="puree">Puree</option>
          <option value="blw">Baby-Led Weaning (BLW)</option>
          <option value="mixed">Mixed</option>
        </select>
      </div>

      <div>
        <label htmlFor="meals_per_day" className="block text-sm font-medium text-gray-700">
          Meals per Day *
        </label>
        <select
          id="meals_per_day"
          required
          value={formData.meals_per_day}
          onChange={(e) => setFormData({ ...formData, meals_per_day: parseInt(e.target.value) })}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        >
          <option value={1}>1 meal</option>
          <option value={2}>2 meals</option>
          <option value={3}>3 meals</option>
        </select>
      </div>

      <div>
        <label htmlFor="dietary_preference" className="block text-sm font-medium text-gray-700">
          Dietary Preference
        </label>
        <select
          id="dietary_preference"
          value={formData.dietary_preference}
          onChange={(e) =>
            setFormData({
              ...formData,
              dietary_preference: e.target.value as 'vegetarian' | 'omnivore',
            })
          }
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        >
          <option value="omnivore">Omnivore</option>
          <option value="vegetarian">Vegetarian</option>
        </select>
      </div>

      <div>
        <label htmlFor="max_prep_minutes" className="block text-sm font-medium text-gray-700">
          Max Prep Time (minutes)
        </label>
        <input
          id="max_prep_minutes"
          type="number"
          min="1"
          value={formData.max_prep_minutes}
          onChange={(e) =>
            setFormData({ ...formData, max_prep_minutes: parseInt(e.target.value) })
          }
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        />
      </div>

      <div>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? 'Creating profile...' : 'Create Profile'}
        </button>
      </div>
    </form>
  )
}


