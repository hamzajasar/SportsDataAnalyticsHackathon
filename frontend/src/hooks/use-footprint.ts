import { useMemo } from 'react'
import { useEmissionFactors, useGridIntensity } from '@/api/queries'
import { COUNTRIES, toGridRows } from '@/lib/footprint'

/** Emission factors as { key: kg CO2e per unit } (UK GHG 2025). */
export function useFactorMap() {
  const factors = useEmissionFactors()
  const map = useMemo(
    () => Object.fromEntries((factors.data ?? []).map((x) => [x.key, x.kg_co2e])),
    [factors.data],
  ) as Record<string, number>
  return { map, isLoading: factors.isLoading }
}

/** Grid CO2 intensity rows for BiH, HR, RS, EU + the latest BiH/EU values. */
export function useGridRows() {
  const grid = useGridIntensity(COUNTRIES, 2010)
  const rows = useMemo(() => toGridRows(grid.data ?? []), [grid.data])
  const latest = rows.at(-1)
  return { grid, rows, latest, bih: latest?.BIH, eu: latest?.EU }
}
