import { Printer, Leaf } from 'lucide-react'
import { useClub } from '@/state/club'
import { useActionPlan, useClubBaseline, useAffordability, useSources } from '@/api/queries'
import { useT } from '@/i18n'
import { QueryState } from '@/components/common/QueryState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatNumber } from '@/lib/format'

const REPORT_NOW = new Date()

export function BoardReportPage() {
  const { club, isSample } = useClub()
  const { t, lang } = useT()
  const actions = useActionPlan(club)
  const baseline = useClubBaseline(club)
  const afford = useAffordability(club)
  const sources = useSources()

  const plan = actions.data
  const base = baseline.data
  const a = afford.data
  const clubName = isSample ? t('common.sampleClub') : (club?.name ?? t('common.yourClub'))
  const top3 = plan?.actions.slice(0, 3) ?? []

  const reportDate = REPORT_NOW.toLocaleDateString(lang === 'bs' ? 'bs-BA' : 'en-GB', {
    year: 'numeric',
    month: 'long',
  })

  return (
    <div className="space-y-6">
      <div className="no-print flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{t('report.title')}</h2>
          <p className="text-sm text-muted-foreground">{t('report.desc')}</p>
        </div>
        <Button onClick={() => window.print()}>
          <Printer className="mr-2 size-4" />
          {t('common.print')}
        </Button>
      </div>

      {/* Printable content */}
      <div className="space-y-6 rounded-lg border p-6 print:border-0 print:p-0">
        {/* Header */}
        <div className="flex items-center justify-between border-b pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Leaf className="size-5 text-primary" />
              <h1 className="text-2xl font-bold">{clubName}</h1>
              {isSample && <Badge variant="secondary">{t('common.example')}</Badge>}
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              {t('report.subtitle')} · {reportDate}
            </p>
          </div>
        </div>

        {/* Summary bar */}
        <QueryState isLoading={actions.isLoading} error={actions.error}>
          <div className="space-y-2">
            <h2 className="font-semibold">{t('report.savings')}</h2>
            <div className="grid grid-cols-3 gap-3">
              {[
                {
                  label: t('report.savePerYear'),
                  value: `${formatNumber(plan?.total_saves_km_year ?? 0)} KM`,
                },
                {
                  label: t('report.cutCo2'),
                  value: `${plan?.total_saves_t_co2_year ?? 0} t/yr`,
                },
                {
                  label: t('report.feeDrop'),
                  value: `−${formatNumber(plan?.fee_drop_per_child_km ?? 0)} KM/yr`,
                },
              ].map((s) => (
                <div key={s.label} className="rounded border p-3">
                  <p className="text-xs text-muted-foreground">{s.label}</p>
                  <p className="text-xl font-bold tabular-nums">{s.value}</p>
                </div>
              ))}
            </div>
          </div>
        </QueryState>

        {/* Top 3 actions */}
        <QueryState isLoading={actions.isLoading} error={actions.error}>
          <div className="space-y-2">
            <h2 className="font-semibold">{t('report.top3')}</h2>
            <ol className="space-y-2">
              {top3.map((act, i) => (
                <li key={act.id} className="rounded border p-3 text-sm">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <span className="text-muted-foreground">{i + 1}. </span>
                      <span className="font-medium">{act.name}</span>
                      <p className="mt-0.5 text-xs text-muted-foreground">{act.basis}</p>
                    </div>
                    <div className="shrink-0 text-right text-xs">
                      <p>{formatNumber(act.saves_km_year)} KM/yr</p>
                      <p>{(act.saves_kg_co2_year / 1000).toFixed(2)} t CO₂/yr</p>
                      <p>
                        {act.payback_years == null
                          ? t('common.free')
                          : t('common.yrPaybackLong', { years: act.payback_years })}
                      </p>
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </QueryState>

        {/* Today's costs */}
        <QueryState isLoading={baseline.isLoading} error={baseline.error}>
          <div className="space-y-2">
            <h2 className="font-semibold">{t('report.todayCosts')}</h2>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded border p-3">
                <p className="text-xs font-medium text-muted-foreground">
                  {t('report.electricity')}
                </p>
                <p>
                  {formatNumber(base?.electricity_km ?? 0)} KM/yr ·{' '}
                  {formatNumber(base?.electricity_kwh ?? 0)} kWh
                </p>
                <p className="text-xs text-muted-foreground">
                  {base?.electricity_t_co2 ?? 0} t CO₂ · {base?.grid_gco2_per_kwh ?? 0} g/kWh (Ember{' '}
                  {base?.grid_year ?? ''})
                </p>
              </div>
              <div className="rounded border p-3">
                <p className="text-xs font-medium text-muted-foreground">
                  {t('report.awayTravel')}
                </p>
                <p>
                  {formatNumber(base?.travel_km_cost ?? 0)} KM/yr ·{' '}
                  {formatNumber(base?.travel_km_driven ?? 0)} km
                </p>
                <p className="text-xs text-muted-foreground">
                  {base?.travel_t_co2 ?? 0} t CO₂ · UK GHG 2025
                </p>
              </div>
            </div>
          </div>
        </QueryState>

        {/* Affordability */}
        <QueryState isLoading={afford.isLoading} error={afford.error}>
          <div className="space-y-2">
            <h2 className="font-semibold">{t('report.affordability')}</h2>
            <p className="text-sm">
              Running cost per child:{' '}
              <strong>{formatNumber(a?.cost_per_child_km ?? 0)} KM/yr</strong> → after upgrades:{' '}
              <strong>{formatNumber(a?.cost_per_child_after_km ?? 0)} KM/yr</strong> (saves{' '}
              {a?.saving_share_pct ?? 0}% of running costs)
            </p>
            <p className="text-xs text-muted-foreground">{a?.note}</p>
          </div>
        </QueryState>

        {/* Sources */}
        <QueryState isLoading={sources.isLoading} error={sources.error}>
          <div className="space-y-2">
            <h2 className="font-semibold">{t('report.dataSources')}</h2>
            <ul className="space-y-0.5 text-xs text-muted-foreground">
              {sources.data?.map((s) => (
                <li key={s.id}>
                  {s.credit ?? s.name}
                  {s.licence ? ` (${s.licence})` : ''}
                </li>
              ))}
            </ul>
          </div>
        </QueryState>
      </div>
    </div>
  )
}
