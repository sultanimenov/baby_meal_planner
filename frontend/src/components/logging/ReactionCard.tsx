'use client'

interface ReactionCardProps {
  id: string
  occurredAt: string
  symptoms: string
  severity: 'mild' | 'moderate' | 'severe'
  suspectedFoodNames: string[]
  notes?: string | null
}

export function ReactionCard({
  occurredAt,
  symptoms,
  severity,
  suspectedFoodNames,
  notes,
}: ReactionCardProps) {
  const severityConfig = {
    mild: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      badge: 'bg-amber-100 text-amber-700',
      icon: '⚠️',
    },
    moderate: {
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      badge: 'bg-orange-100 text-orange-700',
      icon: '⚡',
    },
    severe: {
      bg: 'bg-rose-50',
      border: 'border-rose-200',
      badge: 'bg-rose-100 text-rose-700',
      icon: '🚨',
    },
  }

  const config = severityConfig[severity]

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  return (
    <div
      className={`rounded-xl border ${config.border} ${config.bg} p-4 transition-shadow hover:shadow-md`}
    >
      {/* Header */}
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{config.icon}</span>
          <span className="text-sm text-slate-500">{formatDate(occurredAt)}</span>
        </div>
        <span
          className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${config.badge}`}
        >
          {severity}
        </span>
      </div>

      {/* Symptoms */}
      <p className="mb-3 text-slate-700">{symptoms}</p>

      {/* Suspected Foods */}
      {suspectedFoodNames.length > 0 && (
        <div className="mb-3">
          <p className="mb-1.5 text-xs font-medium uppercase text-slate-500">
            Suspected Foods
          </p>
          <div className="flex flex-wrap gap-1.5">
            {suspectedFoodNames.map((name, idx) => (
              <span
                key={idx}
                className="rounded-full bg-white px-2.5 py-1 text-xs text-slate-600 shadow-sm"
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Notes */}
      {notes && (
        <div className="rounded-lg bg-white/50 p-2.5">
          <p className="text-sm text-slate-600">{notes}</p>
        </div>
      )}
    </div>
  )
}


