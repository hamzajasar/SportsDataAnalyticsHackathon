import { useState } from 'react'
import { Pencil, Plug, Car } from 'lucide-react'
import { useClubBaseline } from '@/api/queries'
import { ClubForm } from '@/components/club/ClubForm'
import { SummaryBar } from '@/components/club/SummaryBar'
import { PageHeader } from '@/components/common/PageHeader'
import { StatCard } from '@/components/common/StatCard'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatNumber } from '@/lib/format'
import { useClub } from '@/state/club'

export function OverviewPage() {
  const { club, requestClub, isSample, isLoading } = useClub()
  const baseline = useClubBaseline(requestClub)
  const [editing, setEditing] = useState(false)
  const b = baseline.data

  return (
    <div className="space-y-6">
      <PageHeader
        title={club?.name ?? 'Your club'}
        description={
          <span className="flex flex-wrap items-center gap-2">
            {isSample ? (
              <Badge variant="outline">Example club — enter your own numbers</Badge>
            ) : (
              <Badge variant="secondary">Your club's numbers</Badge>
            )}
            <span>What running the club costs, and what it could save.</span>
          </span>
        }
        actions={
          <Button variant={editing ? 'secondary' : 'outline'} onClick={() => setEditing((e) => !e)}>
            <Pencil /> {editing ? 'Close' : 'Edit club numbers'}
          </Button>
        }
      />

      {editing && !isLoading && (
        <Card>
          <CardHeader>
            <CardTitle>Your club's numbers</CardTitle>
          </CardHeader>
          <CardContent>
            <ClubForm onDone={() => setEditing(false)} />
          </CardContent>
        </Card>
      )}

      <SummaryBar />

      <div>
        <h2 className="mb-2 text-sm font-medium">Today, every year</h2>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard
            label="Electricity cost"
            value={b ? `${formatNumber(b.electricity_km)} KM` : '–'}
            hint={b ? `${formatNumber(b.electricity_kwh)} kWh` : undefined}
            loading={baseline.isLoading}
          />
          <StatCard
            label="Electricity CO₂"
            value={b ? `${formatNumber(b.electricity_t_co2, 1)} t` : '–'}
            hint={
              b
                ? `BiH grid: ${formatNumber(b.grid_gco2_per_kwh)} g/kWh (${b.grid_year})`
                : undefined
            }
            loading={baseline.isLoading}
          />
          <StatCard
            label="Away travel cost"
            value={b ? `${formatNumber(b.travel_km_cost)} KM` : '–'}
            hint={b ? `${formatNumber(b.travel_km_driven)} km driven` : undefined}
            loading={baseline.isLoading}
          />
          <StatCard
            label="Away travel CO₂"
            value={b ? `${formatNumber(b.travel_t_co2, 1)} t` : '–'}
            hint={
              <span className="inline-flex items-center gap-1">
                <Car className="size-3" /> fuel, cars + minibuses
              </span>
            }
            loading={baseline.isLoading}
          />
        </div>
        <p className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
          <Plug className="size-3" /> Prices: Eurostat (electricity), nafta.hr (fuel). Every source
          is listed under Sources.
        </p>
      </div>
    </div>
  )
}
