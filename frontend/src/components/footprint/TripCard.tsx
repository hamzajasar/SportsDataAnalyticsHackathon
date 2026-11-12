import { useState } from 'react'
import { Bus, Car, TrainFront } from 'lucide-react'
import { useTripComparison } from '@/api/queries'
import { NumberField } from '@/components/common/NumberField'
import { QueryState } from '@/components/common/QueryState'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatNumber } from '@/lib/format'
import { cn } from '@/lib/utils'

const MODE_ICON: Record<string, typeof Car> = {
  cars: Car,
  minibus: Bus,
  coach: Bus,
  rail: TrainFront,
}

/** One away trip: CO2 of cars vs minibuses vs coach vs train (UK GHG 2025). */
export function TripCard() {
  const [distance, setDistance] = useState(120)
  const [people, setPeople] = useState(18)
  const [occupancy, setOccupancy] = useState(3)
  const valid = distance > 0 && people > 0 && occupancy >= 1 && occupancy <= 7
  const trip = useTripComparison(
    {
      distance_km: distance,
      people,
      round_trip: true,
      car_occupancy: occupancy,
      car_type: 'car_average',
    },
    valid,
  )
  const worst = Math.max(...(trip.data?.options.map((o) => o.kg_co2e) ?? [1]))
  return (
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
                    <span className="font-medium tabular-nums">{formatNumber(o.kg_co2e)} kg</span>
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
              Best option saves {formatNumber(trip.data.options[0].saving_vs_worst_kg)} kg CO₂ per
              trip vs the worst. Factors: UK Government GHG conversion factors 2025.
            </p>
          )}
        </QueryState>
      </CardContent>
    </Card>
  )
}
