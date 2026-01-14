'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useAuth } from '@/hooks/use-auth'
import { Navigation } from '@/components/Navigation'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-emerald-50 via-white to-teal-50">
        <div className="text-center">
          <div className="mb-4 inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-emerald-500 border-r-transparent"></div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-emerald-50 via-white to-teal-50 md:flex-row">
      {/* Sidebar navigation (desktop) */}
      <aside className="hidden w-64 shrink-0 md:block">
        <div className="fixed h-full w-64 border-r border-slate-200 bg-white/80 backdrop-blur-lg">
          <div className="p-6">
            <h1 className="text-xl font-bold text-emerald-600">🍼 Meal Planner</h1>
          </div>
          <Navigation />
        </div>
      </aside>
      
      {/* Main content */}
      <main className="flex-1 pb-20 md:pb-0">
        {children}
      </main>
      
      {/* Bottom navigation (mobile) */}
      <div className="md:hidden">
        <Navigation />
      </div>
    </div>
  )
}
