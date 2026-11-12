import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Leaf, Pencil, Zap, Bus, TrendingDown, ArrowRight } from 'lucide-react'
import { useActionPlan, useClubBaseline } from '@/api/queries'
import { useClub } from '@/state/club'
import { ClubForm } from '@/components/club/ClubForm'
import { QueryState } from '@/components/common/QueryState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatNumber } from '@/lib/format'

function StatBlock({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-lg border bg-background p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-muted-foreground">{sub}</p>}
    </div>
  )
}

export function OverviewPage() {
  const navigate = useNavigate()
  const { club, isSample } = useClub()
  const [editOpen, setEditOpen] = useState(false)
  const actions = useActionPlan(club)
  const baseline = useClubBaseline(club)

  const plan = actions.data
  const base = baseline.data
  const top3 = plan?.actions.slice(0, 3) ?? []
  const source = plan ? `Ember ${plan.assumptions.grid_year} · UK GHG 2025` : ''
  const clubName = isSample ? 'Sample Sarajevo club' : (club?.name ?? 'Your club')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-semibold">{clubName}</h1>
          {isSample && <Badge variant="secondary">Example</Badge>}
        </div>
        <Button variant="outline" size="sm" onClick={() => setEditOpen((o) => !o)}>
          <Pencil className="mr-1.5 size-3.5" />
          {editOpen ? 'Close form' : 'Edit club numbers'}
        </Button>
      </div>

      {editOpen && <ClubForm onClose={() => setEditOpen(false)} />}

      {isSample && !editOpen && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-primary/30 bg-primary/5 px-4 py-3">
          <p className="text-sm">
            This is an <span className="font-medium">example Sarajevo club</span>. Enter your own
            numbers to see your real footprint.
          </p>
          <Button size="sm" onClick={() => navigate('/quick-start')}>
            Enter my club <ArrowRight className="ml-1.5 size-3.5" />
          </Button>
        </div>
      )}

      {/* Summary bar */}
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base font-semibold">
            <Leaf className="size-4 text-primary" />
            Potential savings
          </CardTitle>
          {!actions.isLoading && !actions.error && (
            <CardDescription>
              All upgrades combined · {isSample ? 'sample data' : 'your club'} · {source}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          <QueryState isLoading={actions.isLoading} error={actions.error}>
            <div className="space-y-4">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                <StatBlock
                  label="Save per year"
                  value={`${formatNumber(plan?.total_saves_km_year ?? 0)} KM`}
                  sub={source}
                />
                <StatBlock
                  label="Cut CO₂ per year"
                  value={`${plan?.total_saves_t_co2_year ?? 0} t`}
                  sub={source}
                />
                <StatBlock
                  label="Fee drop per child"
                  value={`−${formatNumber(plan?.fee_drop_per_child_km ?? 0)} KM`}
                  sub={`÷ ${plan?.children ?? 0} children · ${source}`}
                />
              </div>

              <div>
                <p className="mb-2 text-sm font-medium">Top 3 actions by payback</p>
                <ol className="space-y-2">
                  {top3.map((action, i) => (
                    <li
                      key={action.id}
                      className="flex flex-col gap-1 rounded-md border bg-background px-3 py-2 text-sm sm:flex-row sm:items-start sm:justify-between sm:gap-4"
                    >
                      <div className="flex min-w-0 items-start gap-2">
                        <span className="mt-0.5 shrink-0 text-xs text-muted-foreground">
                          {i + 1}.
                        </span>
                        <div className="min-w-0">
                          <span className="font-medium">{action.name}</span>
                          <p className="truncate text-xs text-muted-foreground">{action.basis}</p>
                        </div>
                      </div>
                      <div className="flex shrink-0 items-center gap-2 pl-5 sm:pl-0">
                        <span className="text-sm tabular-nums">
                          {formatNumber(action.saves_km_year)} KM/yr
                        </span>
                        <Badge variant={action.payback_years === null ? 'default' : 'secondary'}>
                          {action.payback_years === null
                            ? 'Free'
                            : action.payback_years === 0
                              ? 'Free'
                              : `${action.payback_years} yr`}
                        </Badge>
                      </div>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          </QueryState>
        </CardContent>
      </Card>

      {/* Today's costs */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <Zap className="size-4 text-yellow-500" /> Electricity — today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <QueryState isLoading={baseline.isLoading} error={baseline.error}>
              <div className="grid grid-cols-3 gap-3">
                <StatBlock
                  label="Cost"
                  value={`${formatNumber(base?.electricity_km ?? 0)} KM`}
                  sub="per year"
                />
                <StatBlock
                  label="Usage"
                  value={`${formatNumber(base?.electricity_kwh ?? 0)} kWh`}
                  sub="per year"
                />
                <StatBlock
                  label="CO₂"
                  value={`${base?.electricity_t_co2 ?? 0} t`}
                  sub={`${base?.grid_gco2_per_kwh ?? 0} g/kWh (${base?.grid_year ?? ''})`}
                />
              </div>
            </QueryState>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <Bus className="size-4 text-blue-500" /> Away travel — today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <QueryState isLoading={baseline.isLoading} error={baseline.error}>
              <div className="grid grid-cols-3 gap-3">
                <StatBlock
                  label="Cost"
                  value={`${formatNumber(base?.travel_km_cost ?? 0)} KM`}
                  sub="per year"
                />
                <StatBlock
                  label="Km driven"
                  value={`${formatNumber(base?.travel_km_driven ?? 0)}`}
                  sub="per year"
                />
                <StatBlock label="CO₂" value={`${base?.travel_t_co2 ?? 0} t`} sub="UK GHG 2025" />
              </div>
            </QueryState>
          </CardContent>
        </Card>
      </div>

      {/* All actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            <TrendingDown className="size-4 text-primary" /> All upgrades ranked by payback
          </CardTitle>
          <CardDescription>Shortest payback first — free actions at the top</CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={actions.isLoading}
            error={actions.error}
            isEmpty={(plan?.actions.length ?? 0) === 0}
            empty="No actions available."
          >
            <div className="space-y-1">
              {plan?.actions.map((action) => {
                const pct =
                  plan.total_saves_km_year > 0
                    ? (action.saves_km_year / plan.total_saves_km_year) * 100
                    : 0
                return (
                  <div key={action.id} className="space-y-1 py-2">
                    <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 text-sm">
                      <span className="font-medium">{action.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {formatNumber(action.saves_km_year)} KM/yr ·{' '}
                        {(action.saves_kg_co2_year / 1000).toFixed(2)} t CO₂ ·{' '}
                        {action.cost_km > 0 ? `${formatNumber(action.cost_km)} KM cost` : 'no cost'}
                        {action.payback_years != null
                          ? ` · ${action.payback_years} yr payback`
                          : ''}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">{action.basis}</p>
                    <div className="h-1.5 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </QueryState>
        </CardContent>
      </Card>
    </div>
  )
}
