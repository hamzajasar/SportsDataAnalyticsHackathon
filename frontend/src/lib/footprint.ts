import { formatNumber } from '@/lib/format'

export const COUNTRIES = ['BIH', 'HRV', 'SRB', 'EU']

/** Translate kg CO2 into something a coach can picture. */
export function carKm(kg: number, carFactor: number | undefined) {
  return carFactor ? `≈ ${formatNumber(kg / carFactor)} km by car` : ''
}

type Series = { code: string; points: { year: number; gco2_per_kwh: number }[] }

/** Reshape per-country series into chart rows: [{ year, BIH, HRV, ... }]. */
export function toGridRows(series: Series[]) {
  const byYear = new Map<number, Record<string, number>>()
  for (const s of series)
    for (const p of s.points) {
      const row = byYear.get(p.year) ?? { year: p.year }
      row[s.code] = p.gco2_per_kwh
      byYear.set(p.year, row)
    }
  return [...byYear.values()].sort((a, b) => a.year - b.year)
}
