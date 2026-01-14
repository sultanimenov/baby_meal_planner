'use client'

export function MealFrequencyGuidance() {
  return (
    <div className="rounded-lg bg-blue-50 p-4">
      <h3 className="mb-2 text-sm font-semibold text-blue-900">
        WHO Meal Frequency Guidance
      </h3>
      <div className="space-y-1 text-sm text-blue-800">
        <p>
          <strong>6-8 months:</strong> 2-3 meals per day, plus breast milk or formula
        </p>
        <p>
          <strong>9-11 months:</strong> 3-4 meals per day, plus breast milk or formula
        </p>
        <p>
          <strong>12-24 months:</strong> 3-4 meals per day, plus 1-2 snacks
        </p>
      </div>
      <p className="mt-2 text-xs text-blue-700">
        These are general guidelines. Adjust based on your baby's hunger cues and appetite.
      </p>
    </div>
  )
}


