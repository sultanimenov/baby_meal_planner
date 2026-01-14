'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useAuth } from '@/hooks/use-auth'

interface BabyProfile {
  id: string
  nickname: string
  date_of_birth: string
  feeding_style: string
  meals_per_day: number
  dietary_preference: string
}

interface MealPlan {
  id: string
  start_date: string
  num_days: number
  plan_style: string
  created_at: string
}

export default function DashboardPage() {
  const router = useRouter()
  const { user, loading } = useAuth()
  const [profile, setProfile] = useState<BabyProfile | null>(null)
  const [plans, setPlans] = useState<MealPlan[]>([])
  const [checkingProfile, setCheckingProfile] = useState(true)
  const [loadingPlans, setLoadingPlans] = useState(true)

  useEffect(() => {
    if (!loading && user) {
      loadData()
    }
  }, [user, loading])

  const loadData = async () => {
    // Load profile
    try {
      const profileData = await api.get<BabyProfile>('/baby-profile/me')
      setProfile(profileData)
    } catch (error: any) {
      if (error.message.includes('404') || error.message.includes('not found')) {
        router.push('/onboarding')
        return
      }
      console.error('Error checking profile:', error)
    } finally {
      setCheckingProfile(false)
    }

    // Load recent plans
    try {
      const plansData = await api.get<MealPlan[]>('/plans')
      setPlans(plansData.slice(0, 3)) // Show last 3 plans
    } catch (error) {
      console.error('Error loading plans:', error)
    } finally {
      setLoadingPlans(false)
    }
  }

  // Calculate baby age
  const calculateAge = (dob: string): string => {
    const birthDate = new Date(dob)
    const today = new Date()
    const months = (today.getFullYear() - birthDate.getFullYear()) * 12 + 
                   (today.getMonth() - birthDate.getMonth())
    if (months < 1) return 'Less than 1 month'
    if (months === 1) return '1 month old'
    return `${months} months old`
  }

  if (loading || checkingProfile) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-emerald-500 border-r-transparent"></div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return null // Will redirect to onboarding
  }

  return (
    <div className="p-4 md:p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        {/* Welcome Header */}
        <div className="rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 p-6 text-white shadow-lg">
          <h1 className="text-2xl font-bold md:text-3xl">
            Welcome back! 👋
          </h1>
          <p className="mt-2 opacity-90">
            Ready to plan {profile.nickname}'s next meals?
          </p>
        </div>

        {/* Baby Profile Summary */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-800">
                👶 {profile.nickname}
              </h2>
              <p className="mt-1 text-slate-600">{calculateAge(profile.date_of_birth)}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
                  {profile.feeding_style === 'puree' ? '🥣 Puree' : 
                   profile.feeding_style === 'blw' ? '🖐️ BLW' : '🥄 Mixed'}
                </span>
                <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
                  {profile.meals_per_day} meals/day
                </span>
                <span className="rounded-full bg-amber-100 px-3 py-1 text-sm font-medium text-amber-700">
                  {profile.dietary_preference === 'vegetarian' ? '🥬 Vegetarian' : '🍖 Omnivore'}
                </span>
              </div>
            </div>
            <Link 
              href="/profile/edit"
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50"
            >
              Edit
            </Link>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-2">
          <Link
            href="/plan/new"
            className="group rounded-xl border-2 border-dashed border-emerald-300 bg-emerald-50/50 p-6 transition-all hover:border-emerald-500 hover:bg-emerald-50"
          >
            <div className="text-4xl">✨</div>
            <h3 className="mt-3 text-lg font-semibold text-emerald-700">
              Generate New Plan
            </h3>
            <p className="mt-1 text-sm text-emerald-600">
              Create a personalized 3 or 7-day meal plan
            </p>
          </Link>

          <Link
            href="/today"
            className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-blue-300 hover:shadow-md"
          >
            <div className="text-4xl">📅</div>
            <h3 className="mt-3 text-lg font-semibold text-slate-800">
              Today's Meals
            </h3>
            <p className="mt-1 text-sm text-slate-600">
              View and log today's planned meals
            </p>
          </Link>
        </div>

        {/* Recent Plans */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-800">Recent Plans</h2>
            {plans.length > 0 && (
              <Link 
                href="/plan/new"
                className="text-sm font-medium text-emerald-600 hover:text-emerald-700"
              >
                View all →
              </Link>
            )}
          </div>
          
          {loadingPlans ? (
            <div className="mt-4 text-center text-slate-500">Loading plans...</div>
          ) : plans.length === 0 ? (
            <div className="mt-4 text-center">
              <p className="text-slate-500">No meal plans yet</p>
              <Link 
                href="/plan/new"
                className="mt-2 inline-block text-sm font-medium text-emerald-600 hover:text-emerald-700"
              >
                Create your first plan →
              </Link>
            </div>
          ) : (
            <div className="mt-4 space-y-3">
              {plans.map((plan) => (
                <Link
                  key={plan.id}
                  href={`/plan/${plan.id}`}
                  className="flex items-center justify-between rounded-lg border border-slate-100 p-4 transition-colors hover:bg-slate-50"
                >
                  <div>
                    <div className="font-medium text-slate-800">
                      {plan.num_days}-Day {plan.plan_style === 'variety' ? 'Variety' : 'Simple'} Plan
                    </div>
                    <div className="text-sm text-slate-500">
                      Starting {new Date(plan.start_date).toLocaleDateString()}
                    </div>
                  </div>
                  <span className="text-slate-400">→</span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-3">
          <Link 
            href="/history/foods"
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:shadow-md"
          >
            <div className="text-2xl">🥕</div>
            <div className="mt-2 text-sm font-medium text-slate-600">Food History</div>
            <div className="text-xs text-slate-500">Track introduced foods</div>
          </Link>

          <Link 
            href="/history/reactions"
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:shadow-md"
          >
            <div className="text-2xl">⚠️</div>
            <div className="mt-2 text-sm font-medium text-slate-600">Reactions</div>
            <div className="text-xs text-slate-500">Log any concerns</div>
          </Link>

          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="text-2xl">📊</div>
            <div className="mt-2 text-sm font-medium text-slate-600">Meal Logs</div>
            <div className="text-xs text-slate-500">{plans.length} plans created</div>
          </div>
        </div>
      </div>
    </div>
  )
}
