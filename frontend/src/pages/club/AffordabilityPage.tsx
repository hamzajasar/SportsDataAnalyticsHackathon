import { Bar, BarChart, CartesianGrid, Cell, XAxis, YAxis } from 'recharts'
import { useClub } from '@/state/club'
import { useAffordability } from '@/api/queries'
import { useT } from '@/i18n'
import { QueryState } from '@/components/common/QueryState'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { formatNumber } from '@/lib/format'

export function AffordabilityPage() {
  const { club } = useClub()
  const afford = useAffordability(club)
  const { t } = useT()

  const a = afford.data

  const affordConfig = {
    fee_drop: { label: t('afford.feeDropChartLabel'), color: 'var(--chart-1)' },
  } satisfies ChartConfig

  const barData = (a?.actions ?? []).map((act) => ({
    name: act.name,
    fee_drop: act.fee_drop_per_child_km,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">{t('afford.title')}</h2>
        <p className="text-sm text-muted-foreground">{t('afford.desc')}</p>
      </div>

      {/* Headline */}
      <QueryState isLoading={afford.isLoading} error={afford.error}>
        <div className="rounded-lg border bg-primary/5 p-5">
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground">{t('afford.costToday')}</p>
              <p className="mt-1 text-3xl font-bold tabular-nums">
                {formatNumber(a?.cost_per_child_km ?? 0)} KM
              </p>
              <p className="text-xs text-muted-foreground">{t('afford.perYear')}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{t('afford.afterUpgrades')}</p>
              <p className="mt-1 text-3xl font-bold text-primary tabular-nums">
                {formatNumber(a?.cost_per_child_after_km ?? 0)} KM
              </p>
              <p className="text-xs text-muted-foreground">
                {t('afford.savingPct', { pct: a?.saving_share_pct ?? 0 })}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{t('afford.breakdown')}</p>
              <p className="mt-1 text-sm">
                {t('afford.electricity')}{' '}
                <strong>{formatNumber(a?.electricity_km_year ?? 0)} KM/yr</strong>
              </p>
              <p className="text-sm">
                {t('afford.travel')} <strong>{formatNumber(a?.travel_km_year ?? 0)} KM/yr</strong>
              </p>
              <p className="text-sm">
                {t('afford.total')}{' '}
                <strong>{formatNumber(a?.running_cost_km_year ?? 0)} KM/yr</strong>
              </p>
            </div>
          </div>
        </div>
      </QueryState>

      {/* Per-action bars */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">{t('afford.feeDropTitle')}</CardTitle>
          <CardDescription>{t('afford.feeDropDesc')}</CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={afford.isLoading}
            error={afford.error}
            isEmpty={barData.length === 0}
            empty={t('afford.noActions')}
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
