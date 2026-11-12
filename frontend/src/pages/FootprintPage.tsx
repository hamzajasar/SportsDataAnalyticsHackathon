import { useMemo, useState } from 'react'
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from 'recharts'
import { Bus, Car, Leaf, Shirt, TrainFront, Zap } from 'lucide-react'
import {
  useElectricityMix,
  useEmissionFactors,
  useGridIntensity,
  useTripComparison,
} from '@/api/queries'
import { PageHeader } from '@/components/common/PageHeader'
import { QueryState } from '@/components/common/QueryState'
import { StatCard } from '@/components/common/StatCard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { formatNumber } from '@/lib/format'
import { cn } from '@/lib/utils'

const COUNTRIES = ['BIH', 'HRV', 'SRB', 'EU']
const gridConfig = {
  BIH: { label: 'Bosnia and Herzegovina', color: 'var(--chart-1)' },
  HRV: { label: 'Croatia', color: 'var(--chart-2)' },
  SRB: { label: 'Serbia', color: 'var(--chart-3)' },
  EU: { label: 'EU average', color: 'var(--chart-4)' },
} satisfies ChartConfig

const MODE_ICON: Record<string, typeof Car> = {
  cars: Car,
  minibus: Bus,
  coach: Bus,
  rail: TrainFront,
}

/** Translate kg CO2 into something a coach can picture. */
function carKm(kg: number, carFactor: number | undefined) {
  return carFactor ? `≈ ${formatNumber(kg / carFactor)} km by car` : ''
}

function NumberField({
  id,
  label,
  value,
  onChange,
  min = 0,
  step = 1,
  hint,
}: {
  id: string
  label: string
  value: number
  onChange: (v: number) => void
  min?: number
  step?: number
  hint?: string
}) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type="number"
        inputMode="decimal"
        min={min}
        step={step}
        value={Number.isFinite(value) ? value : ''}
        onChange={(e) => onChange(e.target.valueAsNumber)}
      />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

export function FootprintPage() {
  const grid = useGridIntensity(COUNTRIES, 2010)
  const mix = useElectricityMix('BIH')
  const factors = useEmissionFactors()

  const f = useMemo(
    () => Object.fromEntries((factors.data ?? []).map((x) => [x.key, x.kg_co2e])),
    [factors.data],
  )
  const carFactor = f['car_average']

  // Grid: reshape series -> rows {year, BIH, HRV, ...}
  const gridRows = useMemo(() => {
    const byYear = new Map<number, Record<string, number>>()
    for (const s of grid.data ?? [])
      for (const p of s.points) {
        const row = byYear.get(p.year) ?? { year: p.year }
        row[s.code] = p.gco2_per_kwh
        byYear.set(p.year, row)
      }
    return [...byYear.values()].sort((a, b) => a.year - b.year)
  }, [grid.data])
  const latest = gridRows.at(-1)
  const bih = latest?.BIH
  const eu = latest?.EU

  // Electricity calculator
  const [kwh, setKwh] = useState(20000)
  const kgElec = bih ? (kwh * bih) / 1000 : 0
  const kgElecEu = eu ? (kwh * eu) / 1000 : 0

  // Away trip calculator
  const [distance, setDistance] = useState(120)
  const [people, setPeople] = useState(18)
  const [occupancy, setOccupancy] = useState(3)
  const tripValid = distance > 0 && people > 0 && occupancy >= 1 && occupancy <= 7
  const trip = useTripComparison(
    {
      distance_km: distance,
      people,
      round_trip: true,
      car_occupancy: occupancy,
      car_type: 'car_average',
    },
    tripValid,
  )
  const worst = Math.max(...(trip.data?.options.map((o) => o.kg_co2e) ?? [1]))

  // Kit calculator
  const [kits, setKits] = useState(40)
  const [kgPerKit, setKgPerKit] = useState(0.6)
  const kitNew = kits * kgPerKit * (f['material_clothing_new'] ?? 0)
  const kitReused = kits * kgPerKit * (f['material_clothing_reused'] ?? 0)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Club carbon footprint"
        description="Where a community club's emissions come from — and the cheapest ways to cut them."
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label={`BiH grid, ${latest?.year ?? ''}`}
          value={bih ? `${formatNumber(bih)} g/kWh` : '–'}
          hint="CO₂ per kWh of electricity"
          loading={grid.isLoading}
        />
        <StatCard
          label="vs EU average"
          value={bih && eu ? `${(bih / eu).toFixed(1)}×` : '–'}
          hint="dirtier electricity"
          loading={grid.isLoading}
        />
        <StatCard
          label={`Coal share, ${mix.data?.year ?? ''}`}
          value={mix.data ? `${formatNumber(mix.data.shares_pct.coal ?? 0)}%` : '–'}
          hint="of BiH electricity"
          loading={mix.isLoading}
        />
        <StatCard
          label="New vs re-used kit"
          value={
            f['material_clothing_new'] && f['material_clothing_reused']
              ? `${formatNumber(f['material_clothing_new'] / f['material_clothing_reused'])}×`
              : '–'
          }
          hint="more CO₂ per kg of clothing"
          loading={factors.isLoading}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="size-4" /> How clean is the electricity?
            </CardTitle>
            <CardDescription>Grams of CO₂ per kWh, by year</CardDescription>
          </CardHeader>
          <CardContent>
            <QueryState isLoading={grid.isLoading} error={grid.error}>
              <ChartContainer config={gridConfig} className="h-72 w-full">
                <LineChart data={gridRows} margin={{ left: 0, right: 12 }}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="year" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} width={40} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <ChartLegend content={<ChartLegendContent />} />
                  {COUNTRIES.map((c) => (
                    <Line
                      key={c}
                      dataKey={c}
                      stroke={`var(--color-${c})`}
                      strokeWidth={c === 'BIH' ? 3 : 1.5}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ChartContainer>
            </QueryState>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="size-4" /> Electricity bill → CO₂
            </CardTitle>
            <CardDescription>From the club's yearly kWh (on the electricity bill)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <NumberField id="kwh" label="kWh per year" value={kwh} onChange={setKwh} step={500} />
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-md border p-3">
                <p className="text-muted-foreground">In Bosnia and Herzegovina</p>
                <p className="text-2xl font-semibold tabular-nums">{formatNumber(kgElec)} kg</p>
                <p className="text-xs text-muted-foreground">{carKm(kgElec, carFactor)}</p>
              </div>
              <div className="rounded-md border p-3">
                <p className="text-muted-foreground">Same use on the EU grid</p>
                <p className="text-2xl font-semibold tabular-nums">{formatNumber(kgElecEu)} kg</p>
                <p className="text-xs text-muted-foreground">{carKm(kgElecEu, carFactor)}</p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              Every kWh saved in BiH avoids {bih ? formatNumber(bih) : '–'} g CO₂. Source: Ember.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bus className="size-4" /> Away game: how should the team travel?
            </CardTitle>
            <CardDescription>Round trip, whole squad and staff</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <NumberField
                id="dist"
                label="Distance (km, one way)"
                value={distance}
                onChange={setDistance}
              />
              <NumberField id="people" label="People" value={people} onChange={setPeople} />
              <NumberField
                id="occ"
                label="People per car"
                value={occupancy}
                onChange={setOccupancy}
                min={1}
              />
            </div>
            <QueryState isLoading={trip.isLoading} error={trip.error}>
              <ul className={cn('space-y-2', trip.isFetching && 'opacity-60')}>
                {trip.data?.options.map((o) => {
                  const Icon = MODE_ICON[o.mode] ?? Car
                  return (
                    <li key={o.mode} className="space-y-1">
                      <div className="flex items-center justify-between gap-2 text-sm">
                        <span className="flex items-center gap-2">
                          <Icon className="size-4 text-muted-foreground" /> {o.label}
                        </span>
                        <span className="font-medium tabular-nums">
                          {formatNumber(o.kg_co2e)} kg
                        </span>
                      </div>
                      <div className="h-2 rounded-full bg-muted">
                        <div
                          className="h-2 rounded-full bg-primary"
                          style={{ width: `${(o.kg_co2e / worst) * 100}%` }}
                        />
                      </div>
                    </li>
                  )
                })}
              </ul>
              {trip.data && (
                <p className="mt-3 text-xs text-muted-foreground">
                  Best option saves {formatNumber(trip.data.options[0].saving_vs_worst_kg)} kg CO₂
                  per trip vs the worst. Factors: UK Government GHG conversion factors 2025.
                </p>
              )}
            </QueryState>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shirt className="size-4" /> Kit: buy new or pass it on?
            </CardTitle>
            <CardDescription>
              Footprint of producing the kit a club hands out each season
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <NumberField id="kits" label="Kits per season" value={kits} onChange={setKits} />
              <NumberField
                id="kg"
                label="kg per kit"
                value={kgPerKit}
                onChange={setKgPerKit}
                step={0.1}
                hint="Assumption: shirt + shorts + socks"
              />
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-md border p-3">
                <p className="text-muted-foreground">All new</p>
                <p className="text-2xl font-semibold tabular-nums">{formatNumber(kitNew)} kg</p>
                <p className="text-xs text-muted-foreground">{carKm(kitNew, carFactor)}</p>
              </div>
              <div className="rounded-md border p-3">
                <p className="flex items-center gap-1 text-muted-foreground">
                  <Leaf className="size-3" /> Re-used (kit swap)
                </p>
                <p className="text-2xl font-semibold tabular-nums">{formatNumber(kitReused)} kg</p>
                <p className="text-xs text-muted-foreground">{carKm(kitReused, carFactor)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
