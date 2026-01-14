'use client'

interface FoodDetailModalProps {
  isOpen: boolean
  onClose: () => void
  food: {
    name: string
    category: string
    firstIntroduced: string | null
    ateCount: number
    partialCount: number
    refusedCount: number
    preferenceRatio: number
    hasReaction: boolean
  } | null
}

export function FoodDetailModal({
  isOpen,
  onClose,
  food,
}: FoodDetailModalProps) {
  if (!isOpen || !food) return null

  const totalMeals = food.ateCount + food.partialCount + food.refusedCount

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Unknown'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getPreferenceEmoji = () => {
    if (food.preferenceRatio >= 0.7) return '😋'
    if (food.preferenceRatio >= 0.4) return '😐'
    return '😕'
  }

  const getPreferenceLabel = () => {
    if (food.preferenceRatio >= 0.7) return 'Loves it!'
    if (food.preferenceRatio >= 0.4) return 'Mixed feelings'
    return 'Not a favorite'
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
        {/* Header */}
        <div className="mb-6 text-center">
          <span className="mb-2 block text-4xl">{getPreferenceEmoji()}</span>
          <h2 className="text-2xl font-bold text-slate-900">{food.name}</h2>
          <p className="text-slate-500">{food.category}</p>
        </div>

        {/* Stats grid */}
        <div className="mb-6 grid grid-cols-3 gap-3">
          <div className="rounded-xl bg-emerald-50 p-4 text-center">
            <span className="block text-2xl font-bold text-emerald-600">
              {food.ateCount}
            </span>
            <span className="text-sm text-emerald-700">Ate</span>
          </div>
          <div className="rounded-xl bg-amber-50 p-4 text-center">
            <span className="block text-2xl font-bold text-amber-600">
              {food.partialCount}
            </span>
            <span className="text-sm text-amber-700">Partial</span>
          </div>
          <div className="rounded-xl bg-rose-50 p-4 text-center">
            <span className="block text-2xl font-bold text-rose-600">
              {food.refusedCount}
            </span>
            <span className="text-sm text-rose-700">Refused</span>
          </div>
        </div>

        {/* Preference bar */}
        <div className="mb-6">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="text-slate-600">Preference</span>
            <span className="font-semibold text-slate-900">
              {Math.round(food.preferenceRatio * 100)}% - {getPreferenceLabel()}
            </span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-slate-100">
            <div className="flex h-full">
              {food.ateCount > 0 && (
                <div
                  className="bg-emerald-400"
                  style={{ width: `${(food.ateCount / totalMeals) * 100}%` }}
                />
              )}
              {food.partialCount > 0 && (
                <div
                  className="bg-amber-400"
                  style={{ width: `${(food.partialCount / totalMeals) * 100}%` }}
                />
              )}
              {food.refusedCount > 0 && (
                <div
                  className="bg-rose-400"
                  style={{ width: `${(food.refusedCount / totalMeals) * 100}%` }}
                />
              )}
            </div>
          </div>
        </div>

        {/* Details */}
        <div className="mb-6 space-y-3 rounded-xl bg-slate-50 p-4">
          <div className="flex justify-between">
            <span className="text-slate-600">First introduced</span>
            <span className="font-medium text-slate-900">
              {formatDate(food.firstIntroduced)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-600">Total meals</span>
            <span className="font-medium text-slate-900">{totalMeals}</span>
          </div>
          {food.hasReaction && (
            <div className="flex items-center justify-between rounded-lg bg-rose-100 p-2">
              <span className="text-rose-700">⚠️ Suspected reaction</span>
              <span className="text-sm font-medium text-rose-700">
                Check reaction log
              </span>
            </div>
          )}
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="w-full rounded-lg border border-slate-200 py-3 font-medium text-slate-600 transition-colors hover:bg-slate-50"
        >
          Close
        </button>
      </div>
    </div>
  )
}


