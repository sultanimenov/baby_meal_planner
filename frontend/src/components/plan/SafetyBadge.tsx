'use client'

interface SafetyBadgeProps {
  validated: boolean
  violations?: string[]
}

export function SafetyBadge({ validated, violations = [] }: SafetyBadgeProps) {
  if (validated && violations.length === 0) {
    return (
      <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
        ✓ Safety Validated
      </span>
    )
  }

  if (violations.length > 0) {
    return (
      <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">
        ⚠ Safety Issues
      </span>
    )
  }

  return (
    <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800">
      Pending Validation
    </span>
  )
}


