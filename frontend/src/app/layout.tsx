import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Infant Meal Planner',
  description: 'Plan and manage complementary feeding meals for your baby',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
