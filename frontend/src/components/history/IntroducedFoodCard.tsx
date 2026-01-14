'use client'

interface IntroducedFoodCardProps {
  name: string
  category: string
  firstIntroduced: string | null
  ateCount: number
  partialCount: number
  refusedCount: number
  preferenceRatio: number
  hasReaction: boolean
  onClick?: () => void
}

export function IntroducedFoodCard({
  name,
  category,
  firstIntroduced,
  ateCount,
  partialCount,
  refusedCount,
  preferenceRatio,
  hasReaction,
  onClick,
}: IntroducedFoodCardProps) {
  const totalMeals = ateCount + partialCount + refusedCount

  const getPreferenceColor = () => {
    if (preferenceRatio >= 0.7) return 'text-emerald-600'
    if (preferenceRatio >= 0.4) return 'text-amber-600'
    return 'text-rose-600'
  }

  const getPreferenceLabel = () => {
    if (preferenceRatio >= 0.7) return 'Loves it!'
    if (preferenceRatio >= 0.4) return 'Mixed'
    return 'Not a fan'
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Unknown'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <button
      onClick={onClick}
      className="w-full rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-all hover:border-slate-300 hover:shadow-md"
    >
      <div className="mb-3 flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-slate-900">{name}</h3>
          <p className="text-sm text-slate-500">{category}</p>
        </div>
        <div className="flex items-center gap-2">
          {hasReaction && (
            <span className="rounded-full bg-rose-100 px-2 py-0.5 text-xs font-medium text-rose-700">
              ⚠️ Reaction
            </span>
          )}
          <span
            className={`text-sm font-semibold ${getPreferenceColor()}`}
          >
            {Math.round(preferenceRatio * 100)}%
          </span>
        </div>
      </div>

      {/* Mini stats */}
      <div className="mb-3 flex gap-4 text-xs">
        <div className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
          <span className="text-slate-600">{ateCount} ate</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-amber-400"></span>
          <span className="text-slate-600">{partialCount} partial</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-rose-400"></span>
          <span className="text-slate-600">{refusedCount} refused</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-2 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="flex h-full">
          {ateCount > 0 && (
            <div
              className="bg-emerald-400"
              style={{ width: `${(ateCount / totalMeals) * 100}%` }}
            />
          )}
          {partialCount > 0 && (
            <div
              className="bg-amber-400"
              style={{ width: `${(partialCount / totalMeals) * 100}%` }}
            />
          )}
          {refusedCount > 0 && (
            <div
              className="bg-rose-400"
              style={{ width: `${(refusedCount / totalMeals) * 100}%` }}
            />
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>First tried: {formatDate(firstIntroduced)}</span>
        <span className={getPreferenceColor()}>{getPreferenceLabel()}</span>
      </div>
    </button>
  )
}


