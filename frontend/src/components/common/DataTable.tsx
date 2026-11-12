import { useMemo, useState, type ReactNode } from 'react'
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { compareValues, formatCell } from '@/lib/table'
import { cn } from '@/lib/utils'

export type Column<T> = {
  key: string
  header: ReactNode
  /** Value used for sorting + default rendering */
  value: (row: T) => unknown
  cell?: (row: T) => ReactNode
  align?: 'left' | 'right'
  sortable?: boolean
}

export type SortState = { key: string; desc: boolean } | null

type Props<T> = {
  columns: Column<T>[]
  rows: T[]
  rowKey?: (row: T, index: number) => string | number
  /** Controlled (server-side) sorting. If omitted, sorts client-side. */
  sort?: SortState
  onSortChange?: (sort: SortState) => void
  onRowClick?: (row: T) => void
  className?: string
}

/** Sortable table. Client-side sorting by default; pass sort/onSortChange for server-side. */
export function DataTable<T>({
  columns,
  rows,
  rowKey,
  sort: controlledSort,
  onSortChange,
  onRowClick,
  className,
}: Props<T>) {
  const [localSort, setLocalSort] = useState<SortState>(null)
  const controlled = onSortChange !== undefined
  const sort = controlled ? (controlledSort ?? null) : localSort

  const sorted = useMemo(() => {
    if (controlled || !sort) return rows
    const col = columns.find((c) => c.key === sort.key)
    if (!col) return rows
    const out = [...rows].sort((a, b) => compareValues(col.value(a), col.value(b)))
    return sort.desc ? out.reverse() : out
  }, [rows, columns, sort, controlled])

  const toggle = (key: string) => {
    const next: SortState =
      sort?.key !== key ? { key, desc: false } : sort.desc ? null : { key, desc: true }
    if (controlled) onSortChange(next)
    else setLocalSort(next)
  }

  return (
    <div className={cn('overflow-x-auto rounded-md border', className)}>
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((c) => {
              const active = sort?.key === c.key
              const Icon = !active ? ArrowUpDown : sort.desc ? ArrowDown : ArrowUp
              return (
                <TableHead key={c.key} className={cn(c.align === 'right' && 'text-right')}>
                  {c.sortable === false ? (
                    c.header
                  ) : (
                    <button
                      type="button"
                      onClick={() => toggle(c.key)}
                      className="inline-flex items-center gap-1 hover:text-foreground"
                    >
                      {c.header}
                      <Icon className={cn('size-3', !active && 'opacity-40')} />
                    </button>
                  )}
                </TableHead>
              )
            })}
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((row, i) => (
            <TableRow
              key={rowKey ? rowKey(row, i) : i}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              className={cn(onRowClick && 'cursor-pointer')}
            >
              {columns.map((c) => (
                <TableCell
                  key={c.key}
                  className={cn(
                    'max-w-80 truncate',
                    c.align === 'right' && 'text-right tabular-nums',
                  )}
                >
                  {c.cell ? c.cell(row) : formatCell(c.value(row))}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
