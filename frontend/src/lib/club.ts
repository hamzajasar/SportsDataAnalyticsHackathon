import type { ClubProfile } from '@/api/queries'

/** Pick the ClubProfile fields out of the sample-club JSON (which has extra note fields). */
export function toProfile(raw: Record<string, unknown>): ClubProfile {
  const r = raw as unknown as ClubProfile
  return {
    name: r.name,
    city: r.city,
    lat: r.lat,
    lon: r.lon,
    children: r.children,
    teams: r.teams,
    electricity_kwh_year: { ...r.electricity_kwh_year },
    travel: {
      away_trips_per_team_year: r.travel.away_trips_per_team_year,
      avg_one_way_km: r.travel.avg_one_way_km,
      vehicles_per_trip: { ...r.travel.vehicles_per_trip },
    },
  }
}

/** Returns a list of human-readable problems; empty = valid (mirrors backend limits). */
export function validateClub(c: ClubProfile): string[] {
  const errors: string[] = []
  const nonNeg = (v: number, label: string) => {
    if (!Number.isFinite(v) || v < 0) errors.push(`${label} must be 0 or more`)
  }
  if (!c.name.trim()) errors.push('Club name is required')
  if (!Number.isInteger(c.children) || c.children < 1) errors.push('Children must be at least 1')
  if (!Number.isInteger(c.teams) || c.teams < 1) errors.push('Teams must be at least 1')
  nonNeg(c.electricity_kwh_year.floodlights, 'Floodlights kWh')
  nonNeg(c.electricity_kwh_year.heating, 'Heating kWh')
  nonNeg(c.electricity_kwh_year.hall_and_other, 'Hall & other kWh')
  nonNeg(c.travel.away_trips_per_team_year, 'Away trips')
  nonNeg(c.travel.avg_one_way_km, 'Distance')
  nonNeg(c.travel.vehicles_per_trip.minibus, 'Minibuses')
  nonNeg(c.travel.vehicles_per_trip.car, 'Cars')
  return errors
}
