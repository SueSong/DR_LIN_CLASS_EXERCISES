import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Streaming UI Demo - SSE vs WebSocket',
  description: 'Interactive demo showing different streaming patterns',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

