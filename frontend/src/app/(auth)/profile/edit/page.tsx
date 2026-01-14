'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import { ProfileEditForm } from '@/components/forms/ProfileEditForm'
import type { BabyProfile } from '@/lib/schemas'

export default function ProfileEditPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<BabyProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)

  const loadProfile = async () => {
    try {
      setLoading(true)
      const data = await api.get<BabyProfile>('/baby-profile/me')
      setProfile(data)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProfile()
  }, [])

  const handleSuccess = () => {
    setShowSuccessMessage(true)
    loadProfile()
    
    // Hide success message after 3 seconds
    setTimeout(() => {
      setShowSuccessMessage(false)
    }, 3000)
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50">
        <div className="text-center">
          <div className="mb-4 inline-block h-10 w-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="text-slate-600">Loading profile...</p>
        </div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50">
        <div className="text-center">
          <p className="mb-4 text-rose-600">{error || 'Profile not found'}</p>
          <Link
            href="/onboarding"
            className="rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white transition-colors hover:bg-blue-700"
          >
            Create Profile
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 pb-20">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-slate-100 bg-white/80 px-4 py-4 backdrop-blur-lg">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Edit Profile</h1>
            <p className="text-sm text-slate-500">{profile.nickname}&apos;s settings</p>
          </div>
          <Link
            href="/"
            className="rounded-lg px-4 py-2 text-sm text-slate-600 transition-colors hover:bg-slate-100"
          >
            Cancel
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-lg px-4 pt-6">
        {/* Success message */}
        {showSuccessMessage && (
          <div className="mb-6 rounded-lg bg-emerald-50 p-4 text-emerald-700">
            <div className="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="font-medium">Profile updated successfully!</span>
            </div>
            <p className="mt-1 text-sm">
              Your existing meal plans may not reflect these changes. Consider
              generating a new plan.
            </p>
          </div>
        )}

        {/* Profile info card */}
        <div className="mb-6 rounded-xl bg-white p-4 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-400 to-purple-500 text-2xl text-white">
              {profile.nickname.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                {profile.nickname}
              </h2>
              <p className="text-sm text-slate-500">
                Born{' '}
                {new Date(profile.date_of_birth).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </p>
            </div>
          </div>
        </div>

        {/* Edit form */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <ProfileEditForm
            profile={profile}
            onSuccess={handleSuccess}
            onCancel={() => router.push('/')}
          />
        </div>

        {/* Danger zone */}
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4">
          <h3 className="font-medium text-rose-700">Danger Zone</h3>
          <p className="mt-1 text-sm text-rose-600">
            Deleting your profile will remove all associated meal plans, logs,
            and data.
          </p>
          <button
            onClick={async () => {
              if (
                confirm(
                  'Are you sure you want to delete your baby profile? This action cannot be undone.'
                )
              ) {
                try {
                  await api.delete('/baby-profile/me')
                  router.push('/onboarding')
                } catch (err) {
                  alert('Failed to delete profile')
                }
              }
            }}
            className="mt-3 rounded-lg border border-rose-300 bg-white px-4 py-2 text-sm font-medium text-rose-700 transition-colors hover:bg-rose-100"
          >
            Delete Profile
          </button>
        </div>
      </main>
    </div>
  )
}


