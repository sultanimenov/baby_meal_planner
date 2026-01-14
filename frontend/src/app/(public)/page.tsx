import Link from 'next/link'

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white p-8">
      <div className="w-full max-w-2xl text-center">
        <h1 className="mb-4 text-5xl font-bold text-gray-900">
          Infant Meal Planner
        </h1>
        <p className="mb-8 text-xl text-gray-600">
          Plan safe, nutritious meals for your baby with AI-powered meal planning
        </p>
        <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
          <Link
            href="/signup"
            className="rounded-lg bg-blue-600 px-8 py-3 text-lg font-semibold text-white transition-colors hover:bg-blue-700"
          >
            Get Started
          </Link>
          <Link
            href="/login"
            className="rounded-lg border-2 border-blue-600 px-8 py-3 text-lg font-semibold text-blue-600 transition-colors hover:bg-blue-50"
          >
            Sign In
          </Link>
        </div>
        <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h3 className="mb-2 text-lg font-semibold">Safe & Validated</h3>
            <p className="text-gray-600">
              All meal plans validated against CDC safety guidelines
            </p>
          </div>
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h3 className="mb-2 text-lg font-semibold">Personalized</h3>
            <p className="text-gray-600">
              Tailored to your baby's age, feeding style, and preferences
            </p>
          </div>
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h3 className="mb-2 text-lg font-semibold">Easy to Use</h3>
            <p className="text-gray-600">
              Generate meal plans and shopping lists in minutes
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}


