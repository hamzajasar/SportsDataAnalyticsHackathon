import { describe, expect, it } from 'vitest'
import { toProfile, validateClub } from './club'

const sample = {
  _note: 'illustrative',
  name: 'FK Sample',
  city: 'Sarajevo',
  lat: 43.85,
  lon: 18.41,
  children: 180,
  teams: 6,
  electricity_kwh_year: { floodlights: 22000, heating: 20000, hall_and_other: 10000 },
  heating_note: 'x',
  travel: {
    away_trips_per_team_year: 15,
    avg_one_way_km: 45,
    vehicles_per_trip: { minibus: 1, car: 3 },
  },
  grid_region: 'BiH',
}

describe('club helpers', () => {
  it('keeps only profile fields', () => {
    const p = toProfile(sample)
    expect(p).not.toHaveProperty('_note')
    expect(p).not.toHaveProperty('grid_region')
    expect(p.travel.vehicles_per_trip.car).toBe(3)
  })

  it('accepts the sample club and rejects bad input', () => {
    const p = toProfile(sample)
    expect(validateClub(p)).toEqual([])
    expect(validateClub({ ...p, children: 0 })).toContain('Children must be at least 1')
    expect(validateClub({ ...p, name: ' ' })).toContain('Club name is required')
    const bad = { ...p, electricity_kwh_year: { ...p.electricity_kwh_year, heating: -5 } }
    expect(validateClub(bad)).toContain('Heating kWh must be 0 or more')
  })
})
