import { Leaf } from 'lucide-react'
import { useActionPlan } from '@/api/queries'
import { useClub } from '@/state/club'
import { useT } from '@/i18n'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { QueryState } from '@/components/common/QueryState'
import { formatNumber } from '@/lib/format'

export function SummaryBar() {
  const { club, isSample } = useClub()
  const { data, isLoading, error } = useActionPlan(club)
  const { t } = useT()

  const top3 = data?.actions.slice(0, 3) ?? []
  const source = data ? `Ember ${data.assumptions.grid_year} · UK GHG 2025` : ''

  return (
    <Card className="border-primary/20 bg-primary/5">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <Leaf className="size-4 text-primary" />
          {isSample ? t('summary.titleSample') : t('summary.titleYours')}
          {isSample && <Badge variant="secondary">{t('common.example')}</Badge>}
        </CardTitle>
        {!isLoading && !error && <CardDescription>{t('summary.desc')}</CardDescription>}
      </CardHeader>
      <CardContent>
        <QueryState isLoading={isLoading} error={error}>
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-lg border bg-background p-4">
                <p className="text-sm text-muted-foreground">{t('summary.savePerYear')}</p>
                <p className="mt-1 text-2xl font-semibold tabular-nums">
                  {formatNumber(data?.total_saves_km_year ?? 0)} KM
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">{source}</p>
              </div>
              <div className="rounded-lg border bg-background p-4">
                <p className="text-sm text-muted-foreground">{t('summary.cutCo2')}</p>
                <p className="mt-1 text-2xl font-semibold tabular-nums">
                  {data?.total_saves_t_co2_year ?? 0} t
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">{source}</p>
              </div>
              <div className="rounded-lg border bg-background p-4">
                <p className="text-sm text-muted-foreground">{t('summary.feeDrop')}</p>
                <p className="mt-1 text-2xl font-semibold tabular-nums">
                  −{formatNumber(data?.fee_drop_per_child_km ?? 0)} KM
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {t('summary.children', {
                    children: data?.children ?? 0,
                    source,
                  })}
                </p>
              </div>
            </div>

            <div>
              <p className="mb-2 text-sm font-medium">{t('summary.top3')}</p>
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
                        {formatNumber(action.saves_km_year)} {t('common.kmYr')}
                      </span>
                      <Badge variant={action.payback_years === null ? 'default' : 'secondary'}>
                        {action.payback_years === null
                          ? t('common.free')
                          : t('common.yrPaybackLong', { years: action.payback_years })}
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
  )
}
