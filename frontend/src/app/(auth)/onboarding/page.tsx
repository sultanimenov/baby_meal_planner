'use client'

import { useRouter } from 'next/navigation'
import { BabyProfileForm } from '@/components/forms/BabyProfileForm'

export default function OnboardingPage() {
  const router = useRouter()

  const handleSuccess = () => {
    router.push('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="mx-auto max-w-2xl">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">Welcome!</h1>
          <p className="mt-2 text-gray-600">
            Let's set up your baby's profile to get started with meal planning
          </p>
        </div>
        <div className="rounded-lg bg-white p-8 shadow-sm">
          <BabyProfileForm onSuccess={handleSuccess} />
        </div>
      </div>
    </div>
  )
}

