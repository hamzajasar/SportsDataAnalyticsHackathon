import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useClub, type ClubProfile } from '@/state/club'
import { useSampleClub } from '@/api/queries'
import { useT } from '@/i18n'

function Field({
  id,
  label,
  hint,
  value,
  onChange,
  type = 'number',
  min,
  max,
  step,
  required,
}: {
  id: string
  label: string
  hint?: string
  value: string | number
  onChange: (v: string) => void
  type?: string
  min?: number
  max?: number
  step?: number
  required?: boolean
}) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type={type}
        inputMode={type === 'number' ? 'decimal' : undefined}
        value={value}
        min={min}
        max={max}
        step={step}
        required={required}
        onChange={(e) => onChange(e.target.value)}
      />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

type Draft = {
  name: string
  city: string
  lat: string
  lon: string
  children: string
  teams: string
  floodlights: string
  heating: string
  hall_and_other: string
  away_trips_per_team_year: string
  avg_one_way_km: string
  vehicles_minibus: string
  vehicles_car: string
  pays_electricity: ClubProfile['pays_electricity']
  heating_type: ClubProfile['heating_type']
}

function profileToDraft(p: ClubProfile): Draft {
  return {
    name: p.name,
    city: p.city,
    lat: String(p.lat),
    lon: String(p.lon),
    children: String(p.children),
    teams: String(p.teams),
    floodlights: String(p.electricity_kwh_year.floodlights),
    heating: String(p.electricity_kwh_year.heating),
    hall_and_other: String(p.electricity_kwh_year.hall_and_other),
    away_trips_per_team_year: String(p.travel.away_trips_per_team_year),
    avg_one_way_km: String(p.travel.avg_one_way_km),
    vehicles_minibus: String(p.travel.vehicles_per_trip.minibus),
    vehicles_car: String(p.travel.vehicles_per_trip.car),
    pays_electricity: p.pays_electricity ?? true,
    heating_type: p.heating_type ?? 'electric',
  }
}

function draftToProfile(d: Draft): ClubProfile | null {
  const n = (s: string) => parseFloat(s)
  if (!d.name.trim()) return null
  const lat = n(d.lat)
  const lon = n(d.lon)
  if (isNaN(lat) || lat < 42 || lat > 46) return null
  if (isNaN(lon) || lon < 15 || lon > 20) return null
  const children = parseInt(d.children, 10)
  const teams = parseInt(d.teams, 10)
  if (!children || children < 1 || !teams || teams < 1) return null
  return {
    name: d.name.trim(),
    city: d.city.trim(),
    lat,
    lon,
    children,
    teams,
    electricity_kwh_year: {
      floodlights: Math.max(0, n(d.floodlights) || 0),
      heating: Math.max(0, n(d.heating) || 0),
      hall_and_other: Math.max(0, n(d.hall_and_other) || 0),
    },
    travel: {
      away_trips_per_team_year: Math.max(0, n(d.away_trips_per_team_year) || 0),
      avg_one_way_km: Math.max(0, n(d.avg_one_way_km) || 0),
      vehicles_per_trip: {
        minibus: Math.max(0, n(d.vehicles_minibus) || 0),
        car: Math.max(0, n(d.vehicles_car) || 0),
      },
    },
    pays_electricity: d.pays_electricity,
    heating_type: d.heating_type,
  }
}

const DEFAULT_DRAFT: Draft = {
  name: '',
  city: '',
  lat: '43.85',
  lon: '18.39',
  children: '50',
  teams: '4',
  floodlights: '8000',
  heating: '12000',
  hall_and_other: '4000',
  away_trips_per_team_year: '12',
  avg_one_way_km: '80',
  vehicles_minibus: '1',
  vehicles_car: '3',
  pays_electricity: true,
  heating_type: 'electric',
}

export function ClubForm({ onClose }: { onClose: () => void }) {
  const { club, isSample, setClub, resetToSample } = useClub()
  const sample = useSampleClub()
  const { t } = useT()

  const initialDraft = club
    ? profileToDraft(club)
    : sample.data
      ? profileToDraft(sample.data)
      : DEFAULT_DRAFT

  const [draft, setDraft] = useState<Draft>(initialDraft)
  const [error, setError] = useState<string | null>(null)

  const set = (key: keyof Draft) => (v: string) => setDraft((d) => ({ ...d, [key]: v }))

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const profile = draftToProfile(draft)
    if (!profile) {
      setError(t('form.error'))
      return
    }
    setClub(profile)
    setError(null)
    onClose()
  }

  function handleReset() {
    resetToSample()
    onClose()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{t('form.title')}</CardTitle>
        <CardDescription>{t('form.desc')}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              id="name"
              label={t('form.clubName')}
              value={draft.name}
              onChange={set('name')}
              type="text"
              required
            />
            <Field
              id="city"
              label={t('form.city')}
              value={draft.city}
              onChange={set('city')}
              type="text"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              id="children"
              label={t('form.children')}
              value={draft.children}
              onChange={set('children')}
              min={1}
              step={1}
            />
            <Field
              id="teams"
              label={t('form.teams')}
              value={draft.teams}
              onChange={set('teams')}
              min={1}
              step={1}
            />
          </div>

          <fieldset className="space-y-3 rounded-md border p-4">
            <legend className="px-1 text-sm font-medium">{t('form.electricity')}</legend>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field
                id="floodlights"
                label={t('form.floodlights')}
                value={draft.floodlights}
                onChange={set('floodlights')}
                min={0}
                step={100}
              />
              <Field
                id="heating"
                label={t('form.heating')}
                value={draft.heating}
                onChange={set('heating')}
                min={0}
                step={100}
              />
              <Field
                id="hall"
                label={t('form.hallOther')}
                value={draft.hall_and_other}
                onChange={set('hall_and_other')}
                min={0}
                step={100}
              />
            </div>
          </fieldset>

          <fieldset className="space-y-3 rounded-md border p-4">
            <legend className="px-1 text-sm font-medium">{t('form.awayTravel')}</legend>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field
                id="trips"
                label={t('form.awayTrips')}
                value={draft.away_trips_per_team_year}
                onChange={set('away_trips_per_team_year')}
                min={0}
                step={1}
              />
              <Field
                id="km"
                label={t('form.avgKm')}
                value={draft.avg_one_way_km}
                onChange={set('avg_one_way_km')}
                min={0}
                step={5}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field
                id="minibus"
                label={t('form.minibuses')}
                hint={t('form.minibusHint')}
                value={draft.vehicles_minibus}
                onChange={set('vehicles_minibus')}
                min={0}
                step={1}
              />
              <Field
                id="cars"
                label={t('form.cars')}
                value={draft.vehicles_car}
                onChange={set('vehicles_car')}
                min={0}
                step={1}
              />
            </div>
          </fieldset>

          <details className="text-sm">
            <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
              {t('form.location')}
            </summary>
            <div className="mt-3 grid gap-4 sm:grid-cols-2">
              <Field
                id="lat"
                label={t('form.latitude')}
                value={draft.lat}
                onChange={set('lat')}
                min={42}
                max={46}
                step={0.001}
              />
              <Field
                id="lon"
                label={t('form.longitude')}
                value={draft.lon}
                onChange={set('lon')}
                min={15}
                max={20}
                step={0.001}
              />
            </div>
          </details>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <div className="flex flex-wrap items-center gap-3">
            <Button type="submit">{t('form.submit')}</Button>
            <Button type="button" variant="outline" onClick={handleReset}>
              {isSample ? t('form.resetSample') : t('form.backSample')}
            </Button>
            <Button type="button" variant="ghost" onClick={onClose}>
              {t('form.cancel')}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
