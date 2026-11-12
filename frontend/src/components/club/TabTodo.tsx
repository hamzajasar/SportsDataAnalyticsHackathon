import type { ReactNode } from 'react'

/** Dev-only note on unfinished tabs (never shown in a production build). */
export function TabTodo({ children }: { children: ReactNode }) {
  if (!import.meta.env.DEV) return null
  return (
    <div className="rounded-md border border-dashed p-3 text-xs text-muted-foreground">
      <b>To do (dev only):</b> {children}
    </div>
  )
}
