import { fireEvent, render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { compareValues } from '@/lib/table'
import { DataTable, type Column } from './DataTable'

type Row = { name: string; goals: number | null }
const rows: Row[] = [
  { name: 'Bears', goals: 3 },
  { name: 'Lions', goals: null },
  { name: 'Owls', goals: 10 },
]
const columns: Column<Row>[] = [
  { key: 'name', header: 'Team', value: (r) => r.name },
  { key: 'goals', header: 'Goals', value: (r) => r.goals, align: 'right' },
]

const firstColumn = () =>
  screen
    .getAllByRole('row')
    .slice(1)
    .map((r) => within(r).getAllByRole('cell')[0].textContent)

describe('DataTable', () => {
  it('sorts client-side asc -> desc -> off, nulls last', () => {
    render(<DataTable columns={columns} rows={rows} />)
    const goals = screen.getByRole('button', { name: /goals/i })
    fireEvent.click(goals)
    expect(firstColumn()).toEqual(['Bears', 'Owls', 'Lions'])
    fireEvent.click(goals)
    expect(firstColumn()).toEqual(['Lions', 'Owls', 'Bears'])
    fireEvent.click(goals)
    expect(firstColumn()).toEqual(['Bears', 'Lions', 'Owls'])
  })

  it('compares numbers numerically and strings naturally', () => {
    expect(compareValues(2, 10)).toBeLessThan(0)
    expect(compareValues('item2', 'item10')).toBeLessThan(0)
    expect(compareValues(null, 1)).toBeGreaterThan(0)
  })
})
