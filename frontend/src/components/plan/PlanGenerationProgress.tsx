'use client'

export function PlanGenerationProgress() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md text-center">
        <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
        <h2 className="mb-2 text-xl font-bold text-gray-900">Generating Your Meal Plan</h2>
        <p className="mb-4 text-gray-600">
          Our AI is creating a personalized, safety-validated meal plan for your baby...
        </p>
        <div className="space-y-2 text-sm text-gray-500">
          <p>✓ Loading your baby's profile</p>
          <p>✓ Selecting age-appropriate recipes</p>
          <p>✓ Validating safety guidelines</p>
          <p className="animate-pulse">⏳ Generating meal plan...</p>
        </div>
        <p className="mt-6 text-xs text-gray-500">
          This may take up to 30 seconds
        </p>
      </div>
    </div>
  )
}


