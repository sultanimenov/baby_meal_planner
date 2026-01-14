'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { ReactionCard } from '@/components/logging/ReactionCard'
import { ReactionLogForm } from '@/components/logging/ReactionLogForm'

interface ReactionLog {
  id: string
  occurred_at: string
  symptoms: string
  severity: 'mild' | 'moderate' | 'severe'
  suspected_food_ids: string[]
  suspected_food_names: string[]
  suspected_recipe_ids: string[]
  suspected_recipe_titles: string[]
  notes: string | null
  created_at: string
}

export default function ReactionHistoryPage() {
  const [reactions, setReactions] = useState<ReactionLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)

  const loadReactions = async () => {
    try {
      setLoading(true)
      const data = await api.get<ReactionLog[]>('/logs/reaction')
      setReactions(data)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reactions')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadReactions()
  }, [])

  const handleFormSuccess = () => {
    setShowForm(false)
    loadReactions()
  }

  // Group reactions by month
  const groupedReactions = reactions.reduce(
    (acc, reaction) => {
      const date = new Date(reaction.occurred_at)
      const monthKey = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
      })
      if (!acc[monthKey]) {
        acc[monthKey] = []
      }
      acc[monthKey].push(reaction)
      return acc
    },
    {} as Record<string, ReactionLog[]>
  )

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-white to-rose-50">
        <div className="text-center">
          <div className="mb-4 inline-block h-10 w-10 animate-spin rounded-full border-4 border-rose-600 border-t-transparent"></div>
          <p className="text-slate-600">Loading reactions...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-rose-50 pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-slate-100 bg-white/80 px-4 py-4 backdrop-blur-lg">
        <div className="mx-auto flex max-w-2xl items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Reaction Log</h1>
            <p className="text-sm text-slate-500">Track suspected food reactions</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-rose-700"
          >
            + Log Reaction
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-2xl px-4 pt-6">
        {error && (
          <div className="mb-6 rounded-lg bg-rose-50 p-4 text-rose-700">
            {error}
          </div>
        )}

        {/* Form Modal */}
        {showForm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div
              className="absolute inset-0 bg-black/50 backdrop-blur-sm"
              onClick={() => setShowForm(false)}
            />
            <div className="relative z-10 mx-4 max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white p-6 shadow-xl">
              <h2 className="mb-4 text-xl font-bold text-slate-900">
                Log New Reaction
              </h2>
              <ReactionLogForm
                onSuccess={handleFormSuccess}
                onCancel={() => setShowForm(false)}
              />
            </div>
          </div>
        )}

        {/* Reactions list */}
        {reactions.length > 0 ? (
          <div className="space-y-8">
            {Object.entries(groupedReactions).map(([month, monthReactions]) => (
              <div key={month}>
                <h2 className="mb-4 text-sm font-semibold uppercase text-slate-500">
                  {month}
                </h2>
                <div className="space-y-4">
                  {monthReactions.map((reaction) => (
                    <ReactionCard
                      key={reaction.id}
                      id={reaction.id}
                      occurredAt={reaction.occurred_at}
                      symptoms={reaction.symptoms}
                      severity={reaction.severity}
                      suspectedFoodNames={reaction.suspected_food_names || []}
                      notes={reaction.notes}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
            <div className="mb-4 text-4xl">✨</div>
            <p className="mb-2 font-medium text-slate-700">No reactions logged</p>
            <p className="mb-4 text-sm text-slate-500">
              Track any suspected food reactions to help identify allergies
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-block rounded-lg bg-rose-600 px-6 py-2.5 font-medium text-white transition-colors hover:bg-rose-700"
            >
              Log First Reaction
            </button>
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
            href="/history/foods"
            className="flex-1 rounded-xl border border-slate-200 bg-white py-3 text-center font-medium text-slate-600 shadow-sm transition-all hover:border-slate-300 hover:shadow"
          >
            Food History
          </Link>
        </div>
      </main>
    </div>
  )
}


