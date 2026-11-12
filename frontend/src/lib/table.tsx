import type { ReactNode } from 'react'

/** Sort comparator: numbers numerically, strings naturally (item2 < item10), nulls last. */
export function compareValues(a: unknown, b: unknown): number {
  if (a == null && b == null) return 0
  if (a == null) return 1
  if (b == null) return -1
  if (typeof a === 'number' && typeof b === 'number') return a - b
  return String(a).localeCompare(String(b), undefined, { numeric: true })
}

export function formatCell(v: unknown): ReactNode {
  if (v == null) return <span className="text-muted-foreground/60">—</span>
  if (typeof v === 'number') return Number.isInteger(v) ? v : Number(v.toFixed(4))
  if (typeof v === 'boolean') return v ? 'true' : 'false'
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}
