import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Child Growth Assistant',
  description: 'Parenting coach for child growth and mentorship',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}


