'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { getCurrentUser, logout } from '@/lib/auth'
import type { User } from '@/lib/schemas'

export function useAuth() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      setUser(null)
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return {
    user,
    loading,
    isAuthenticated: !!user,
    logout: handleLogout,
    refresh: checkAuth,
  }
}


