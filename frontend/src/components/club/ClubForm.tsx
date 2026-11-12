import { useState, type ReactNode } from 'react'
import type { ClubProfile } from '@/api/queries'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { validateClub } from '@/lib/club'
import { useClub } from '@/state/club'

function Field({
  id,
  label,
  value,
  onChange,
  hint,
  step = 1,
}: {
  id: string
  label: string
  value: number
  onChange: (v: number) => void
  hint?: string
  step?: number
}) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type="number"
        inputMode="decimal"
        min={0}
        step={step}
        value={Number.isFinite(value) ? value : ''}
        onChange={(e) => onChange(e.target.valueAsNumber)}
      />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

function Group({ title, children }: { title: string; children: ReactNode }) {
  return (
    <fieldset className="grid gap-3">
      <legend className="mb-1 text-sm font-medium">{title}</legend>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">{children}</div>
    </fieldset>
  )
}

/** Edit the club's own numbers; every tab recalculates from them. */
export function ClubForm({ onDone }: { onDone?: () => void }) {
  const { club, setClub, resetToSample, isSample } = useClub()
  const [draft, setDraft] = useState<ClubProfile | null>(club)
  if (!draft) return null

  const errors = validateClub(draft)
  const set = (patch: Partial<ClubProfile>) => setDraft({ ...draft, ...patch })
  const setKwh = (k: keyof ClubProfile['electricity_kwh_year'], v: number) =>
    set({ electricity_kwh_year: { ...draft.electricity_kwh_year, [k]: v } })
  const setTravel = (patch: Partial<ClubProfile['travel']>) =>
    set({ travel: { ...draft.travel, ...patch } })
  const setVehicles = (k: 'minibus' | 'car', v: number) =>
    setTravel({ vehicles_per_trip: { ...draft.travel.vehicles_per_trip, [k]: v } })

  return (
    <form
      className="grid gap-5"
      onSubmit={(e) => {
        e.preventDefault()
        if (errors.length) return
        setClub(draft)
        onDone?.()
      }}
    >
      <Group title="Club">
        <div className="col-span-2 grid gap-1.5">
          <Label htmlFor="club-name">Name</Label>
          <Input
            id="club-name"
            value={draft.name}
            onChange={(e) => set({ name: e.target.value })}
          />
        </div>
        <Field
          id="children"
          label="Children"
          value={draft.children}
          onChange={(v) => set({ children: v })}
        />
        <Field id="teams" label="Teams" value={draft.teams} onChange={(v) => set({ teams: v })} />
      </Group>

      <Group title="Electricity per year (kWh, from the bills)">
        <Field
          id="flood"
          label="Floodlights"
          value={draft.electricity_kwh_year.floodlights}
          onChange={(v) => setKwh('floodlights', v)}
          step={500}
        />
        <Field
          id="heat"
          label="Heating"
          value={draft.electricity_kwh_year.heating}
          onChange={(v) => setKwh('heating', v)}
          step={500}
        />
        <Field
          id="hall"
          label="Hall & other"
          value={draft.electricity_kwh_year.hall_and_other}
          onChange={(v) => setKwh('hall_and_other', v)}
          step={500}
        />
      </Group>

      <Group title="Away games">
        <Field
          id="trips"
          label="Away trips per team / year"
          value={draft.travel.away_trips_per_team_year}
          onChange={(v) => setTravel({ away_trips_per_team_year: v })}
        />
        <Field
          id="km"
          label="Average distance (km, one way)"
          value={draft.travel.avg_one_way_km}
          onChange={(v) => setTravel({ avg_one_way_km: v })}
        />
        <Field
          id="minibus"
          label="Minibuses per trip"
          value={draft.travel.vehicles_per_trip.minibus}
          onChange={(v) => setVehicles('minibus', v)}
        />
        <Field
          id="cars"
          label="Cars per trip"
          value={draft.travel.vehicles_per_trip.car}
          onChange={(v) => setVehicles('car', v)}
        />
      </Group>

      {errors.length > 0 && (
        <ul className="list-disc pl-5 text-sm text-destructive">
          {errors.map((e) => (
            <li key={e}>{e}</li>
          ))}
        </ul>
      )}

      <div className="flex flex-wrap gap-2">
        <Button type="submit" disabled={errors.length > 0}>
          Calculate for this club
        </Button>
        {!isSample && (
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              resetToSample()
              onDone?.()
            }}
          >
            Back to the example club
          </Button>
        )}
      </div>
    </form>
  )
}
