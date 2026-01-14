'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: '🏠' },
  { href: '/plan/new', label: 'New Plan', icon: '✨' },
  { href: '/today', label: 'Today', icon: '📅' },
  { href: '/history/foods', label: 'Foods', icon: '🥕' },
  { href: '/history/reactions', label: 'Reactions', icon: '⚠️' },
  { href: '/profile/edit', label: 'Profile', icon: '👶' },
]

export function Navigation() {
  const pathname = usePathname()
  const { logout } = useAuth()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-slate-200 bg-white/95 backdrop-blur-lg md:relative md:border-r md:border-t-0">
      <div className="flex justify-around md:flex-col md:justify-start md:gap-1 md:p-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-1 px-3 py-2 text-xs transition-colors md:flex-row md:gap-3 md:rounded-lg md:px-4 md:py-3 md:text-sm ${
                isActive
                  ? 'text-emerald-600 md:bg-emerald-50'
                  : 'text-slate-600 hover:text-emerald-600 md:hover:bg-slate-50'
              }`}
            >
              <span className="text-lg md:text-base">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          )
        })}
        <button
          onClick={logout}
          className="flex flex-col items-center gap-1 px-3 py-2 text-xs text-slate-600 transition-colors hover:text-red-600 md:mt-auto md:flex-row md:gap-3 md:rounded-lg md:px-4 md:py-3 md:text-sm md:hover:bg-red-50"
        >
          <span className="text-lg md:text-base">🚪</span>
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </nav>
  )
}


