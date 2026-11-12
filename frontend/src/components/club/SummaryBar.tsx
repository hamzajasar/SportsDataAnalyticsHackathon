import { ArrowRight, Clock, Leaf, Wallet } from 'lucide-react'
import { useActionPlan } from '@/api/queries'
import { QueryState } from '@/components/common/QueryState'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatNumber } from '@/lib/format'
import { cn } from '@/lib/utils'
import { useClub } from '@/state/club'

function payback(years: number | null) {
  if (years === null) return 'no saving'
  if (years === 0) return 'free — saves from day one'
  return `pays back in ${years.toLocaleString(undefined, { maximumFractionDigits: 1 })} years`
}

/** The headline: what the club could save per year, and the 3 best actions (by payback). */
export function SummaryBar() {
  const { requestClub } = useClub()
  const plan = useActionPlan(requestClub)
  const d = plan.data

  return (
    <QueryState isLoading={plan.isLoading} error={plan.error}>
      {d && (
        <div className={cn('space-y-4', plan.isFetching && 'opacity-70')}>
          <div className="grid gap-4 rounded-xl bg-primary p-5 text-primary-foreground sm:grid-cols-3">
            <div>
              <p className="flex items-center gap-1.5 text-sm opacity-80">
                <Wallet className="size-4" /> Could save
              </p>
              <p className="text-3xl font-semibold tabular-nums">
                {formatNumber(d.total_saves_km_year)} KM
              </p>
              <p className="text-sm opacity-80">per year</p>
            </div>
            <div>
              <p className="flex items-center gap-1.5 text-sm opacity-80">
                <Leaf className="size-4" /> Less CO₂
              </p>
              <p className="text-3xl font-semibold tabular-nums">
                {formatNumber(d.total_saves_t_co2_year, 1)} t
              </p>
              <p className="text-sm opacity-80">per year</p>
            </div>
            <div>
              <p className="text-sm opacity-80">Membership fee could drop by</p>
              <p className="text-3xl font-semibold tabular-nums">
                {formatNumber(d.fee_drop_per_child_km, 1)} KM
              </p>
              <p className="text-sm opacity-80">per child, per year ({d.children} children)</p>
            </div>
          </div>

          <div>
            <h2 className="mb-2 text-sm font-medium">Do these first</h2>
            <div className="grid gap-3 md:grid-cols-3">
              {d.actions.slice(0, 3).map((a, i) => (
                <Card key={a.id}>
                  <CardHeader>
                    <CardDescription className="flex items-center justify-between">
                      <span>#{i + 1}</span>
                      <Badge variant="secondary" className="gap-1">
                        <Clock className="size-3" /> {payback(a.payback_years)}
                      </Badge>
                    </CardDescription>
                    <CardTitle>{a.name}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-1 text-sm">
                    <p>
                      Saves <b className="tabular-nums">{formatNumber(a.saves_km_year)} KM</b> and{' '}
                      <b className="tabular-nums">
                        {formatNumber(a.saves_kg_co2_year / 1000, 1)} t CO₂
                      </b>{' '}
                      a year
                    </p>
                    <p className="text-muted-foreground">
                      Costs {a.cost_km ? `${formatNumber(a.cost_km)} KM` : 'nothing'}
                    </p>
                    <p className="flex items-start gap-1 text-xs text-muted-foreground">
                      <ArrowRight className="mt-0.5 size-3 shrink-0" /> {a.basis}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}
    </QueryState>
  )
}
