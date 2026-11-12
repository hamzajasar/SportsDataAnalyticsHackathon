import { useMemo, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, XAxis, YAxis } from 'recharts'
import { Shirt, Leaf } from 'lucide-react'
import { useClub } from '@/state/club'
import { useAffordability, useEmissionFactors } from '@/api/queries'
import { QueryState } from '@/components/common/QueryState'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { formatNumber } from '@/lib/format'

const affordConfig = {
  fee_drop: { label: 'Fee drop (KM/child)', color: 'var(--chart-1)' },
} satisfies ChartConfig

function carKm(kg: number, factor: number | undefined) {
  return factor ? `≈ ${formatNumber(kg / factor)} km by car` : ''
}

export function AffordabilityPage() {
  const { club } = useClub()
  const afford = useAffordability(club)
  const factors = useEmissionFactors()
  const f = useMemo(
    () => Object.fromEntries((factors.data ?? []).map((x) => [x.key, x.kg_co2e])),
    [factors.data],
  )
  const carFactor = f['car_average']

  // Kit calculator
  const [kits, setKits] = useState(40)
  const [kgPerKit, setKgPerKit] = useState(0.6)
  const kitNew = kits * kgPerKit * (f['material_clothing_new'] ?? 0)
  const kitReused = kits * kgPerKit * (f['material_clothing_reused'] ?? 0)

  const a = afford.data
  const barData = (a?.actions ?? []).map((act) => ({
    name: act.name,
    fee_drop: act.fee_drop_per_child_km,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Affordability</h2>
        <p className="text-sm text-muted-foreground">
          How much does running the club cost per child — and what can lower it?
        </p>
      </div>

      {/* Headline */}
      <QueryState isLoading={afford.isLoading} error={afford.error}>
        <div className="rounded-lg border bg-primary/5 p-5">
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground">Cost per child today</p>
              <p className="mt-1 text-3xl font-bold tabular-nums">
                {formatNumber(a?.cost_per_child_km ?? 0)} KM
              </p>
              <p className="text-xs text-muted-foreground">per year</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">After all upgrades</p>
              <p className="mt-1 text-3xl font-bold text-primary tabular-nums">
                {formatNumber(a?.cost_per_child_after_km ?? 0)} KM
              </p>
              <p className="text-xs text-muted-foreground">
                saves {a?.saving_share_pct ?? 0}% of running costs
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Running cost breakdown</p>
              <p className="mt-1 text-sm">
                Electricity: <strong>{formatNumber(a?.electricity_km_year ?? 0)} KM/yr</strong>
              </p>
              <p className="text-sm">
                Travel: <strong>{formatNumber(a?.travel_km_year ?? 0)} KM/yr</strong>
              </p>
              <p className="text-sm">
                Total: <strong>{formatNumber(a?.running_cost_km_year ?? 0)} KM/yr</strong>
              </p>
            </div>
          </div>
        </div>
      </QueryState>

      {/* Per-action bars */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Fee drop per child — by action</CardTitle>
          <CardDescription>KM saved per child per year for each upgrade</CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={afford.isLoading}
            error={afford.error}
            isEmpty={barData.length === 0}
            empty="No actions available."
          >
            <ChartContainer config={affordConfig} className="h-64 w-full">
              <BarChart data={barData} layout="vertical" margin={{ left: 8, right: 32 }}>
                <CartesianGrid horizontal={false} />
                <XAxis type="number" tickLine={false} axisLine={false} />
                <YAxis
                  dataKey="name"
                  type="category"
                  tickLine={false}
                  axisLine={false}
                  width={120}
                  tick={{ fontSize: 12 }}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="fee_drop" radius={4}>
                  {barData.map((_, i) => (
                    <Cell key={i} fill={`var(--chart-${(i % 5) + 1})`} />
                  ))}
                </Bar>
              </BarChart>
            </ChartContainer>
          </QueryState>
        </CardContent>
      </Card>

      {a && (
        <div className="space-y-1 text-xs text-muted-foreground">
          <p>{a.scope}</p>
          <p>{a.note}</p>
        </div>
      )}

      {/* Kit calculator */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            <Shirt className="size-4" /> Kit: buy new or pass it on?
          </CardTitle>
          <CardDescription>
            Footprint of producing the kit a club hands out each season
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="kits">Kits per season</Label>
              <Input
                id="kits"
                type="number"
                inputMode="decimal"
                min={0}
                value={kits}
                onChange={(e) => setKits(Number(e.target.value) || 0)}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="kgk">kg per kit</Label>
              <Input
                id="kgk"
                type="number"
                inputMode="decimal"
                min={0}
                step={0.1}
                value={kgPerKit}
                onChange={(e) => setKgPerKit(Number(e.target.value) || 0)}
              />
              <p className="text-xs text-muted-foreground">Assumption: shirt + shorts + socks</p>
            </div>
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
          <p className="text-xs text-muted-foreground">
            Factors: UK Government GHG Conversion Factors 2025 (OGL v3.0).
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
