import { Bar, BarChart, CartesianGrid, Cell, XAxis, YAxis } from 'recharts'
import { useClub } from '@/state/club'
import { useAffordability } from '@/api/queries'
import { QueryState } from '@/components/common/QueryState'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { formatNumber } from '@/lib/format'

const affordConfig = {
  fee_drop: { label: 'Fee drop (KM/child)', color: 'var(--chart-1)' },
} satisfies ChartConfig

export function AffordabilityPage() {
  const { club } = useClub()
  const afford = useAffordability(club)

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
    </div>
  )
}
