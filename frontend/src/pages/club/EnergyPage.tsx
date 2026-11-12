import { useMemo, useState } from 'react'
import { Bar, CartesianGrid, ComposedChart, Legend, Line, LineChart, XAxis, YAxis } from 'recharts'
import { useClub } from '@/state/club'
import { useEnergyProfile, useGridIntensity, useElectricityMix } from '@/api/queries'
import { useT } from '@/i18n'
import { QueryState } from '@/components/common/QueryState'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { formatNumber, monthName } from '@/lib/format'

const COUNTRIES = ['BIH', 'HRV', 'SRB', 'EU']

export function EnergyPage() {
  const { club } = useClub()
  const [kwp, setKwp] = useState(0)
  const energy = useEnergyProfile(club, kwp)
  const grid = useGridIntensity(COUNTRIES, 2010)
  const mix = useElectricityMix('BIH')
  const { t } = useT()

  const profile = energy.data

  const energyConfig = {
    heating_kwh: { label: t('energy.heating'), color: 'var(--chart-1)' },
    floodlights_kwh: { label: t('energy.floodlights'), color: 'var(--chart-2)' },
    hall_kwh: { label: t('energy.hallOther'), color: 'var(--chart-3)' },
    solar_used_kwh: { label: t('energy.solarUsed'), color: 'var(--chart-4)' },
  } satisfies ChartConfig

  const gridConfig = {
    BIH: { label: t('energy.bosniaLabel'), color: 'var(--chart-1)' },
    HRV: { label: t('energy.croatiaLabel'), color: 'var(--chart-2)' },
    SRB: { label: t('energy.serbiaLabel'), color: 'var(--chart-3)' },
    EU: { label: t('energy.euLabel'), color: 'var(--chart-4)' },
  } satisfies ChartConfig

  const chartData = useMemo(
    () =>
      (profile?.months ?? []).map((m, i) => ({
        month: monthName(i, 'short'),
        heating_kwh: m.heating_kwh,
        floodlights_kwh: m.floodlights_kwh,
        hall_kwh: m.hall_kwh,
        solar_used_kwh: kwp > 0 ? m.solar_used_kwh : undefined,
        mean_temp_c: m.mean_temp_c,
      })),
    [profile, kwp],
  )

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

  const descKey = profile?.illustrative_club ? 'energy.descSample' : 'energy.descYours'

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">{t('energy.title')}</h2>
          <p className="text-sm text-muted-foreground">{t(descKey)}</p>
        </div>
        <div className="flex items-end gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor="kwp">{t('energy.solarLabel')}</Label>
            <Input
              id="kwp"
              type="number"
              inputMode="decimal"
              min={0}
              max={50}
              step={1}
              value={kwp}
              className="w-28"
              onChange={(e) => setKwp(Math.max(0, Math.min(50, Number(e.target.value) || 0)))}
            />
          </div>
        </div>
      </div>

      {/* Totals */}
      <QueryState isLoading={energy.isLoading} error={energy.error}>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            { label: t('energy.netKwh'), value: formatNumber(profile?.totals.net_kwh ?? 0) },
            {
              label: t('energy.costYr'),
              value: `${formatNumber(profile?.totals.cost_km ?? 0)} KM`,
            },
            {
              label: t('energy.co2Yr'),
              value: `${((profile?.totals.co2_kg ?? 0) / 1000).toFixed(1)} t`,
            },
            ...(kwp > 0
              ? [
                  {
                    label: t('energy.solarProduced'),
                    value: `${formatNumber(profile?.totals.solar_produced_kwh ?? 0)} kWh`,
                  },
                ]
              : []),
          ].map((s) => (
            <div key={s.label} className="rounded-lg border bg-card p-3">
              <p className="text-xs text-muted-foreground">{s.label}</p>
              <p className="mt-0.5 text-xl font-semibold tabular-nums">{s.value}</p>
            </div>
          ))}
        </div>
      </QueryState>

      {/* Monthly chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">{t('energy.monthlyTitle')}</CardTitle>
          <CardDescription>
            {kwp > 0 ? t('energy.solarDesc', { kwp }) : t('energy.monthlyDesc')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState isLoading={energy.isLoading} error={energy.error}>
            <ChartContainer config={energyConfig} className="h-72 w-full">
              <ComposedChart data={chartData} margin={{ left: 0, right: 8 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} width={50} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend />
                <Bar dataKey="heating_kwh" stackId="a" fill="var(--color-heating_kwh)" />
                <Bar dataKey="floodlights_kwh" stackId="a" fill="var(--color-floodlights_kwh)" />
                <Bar dataKey="hall_kwh" stackId="a" fill="var(--color-hall_kwh)" />
                {kwp > 0 && (
                  <Line
                    dataKey="solar_used_kwh"
                    stroke="var(--color-solar_used_kwh)"
                    strokeWidth={2}
                    dot={false}
                    type="monotone"
                  />
                )}
              </ComposedChart>
            </ChartContainer>
          </QueryState>
        </CardContent>
      </Card>

      {profile && <p className="text-xs text-muted-foreground">{profile.method.join(' · ')}</p>}

      {/* Grid intensity chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">{t('energy.gridTitle')}</CardTitle>
          <CardDescription>
            Grams of CO₂ per kWh · BiH {latest?.BIH ? `${formatNumber(latest.BIH)} g/kWh` : ''} in{' '}
            {latest?.year ?? ''}
            {mix.data ? ` · ${formatNumber(mix.data.shares_pct.coal ?? 0)}% coal` : ''}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState isLoading={grid.isLoading} error={grid.error}>
            <ChartContainer config={gridConfig} className="h-64 w-full">
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
    </div>
  )
}
