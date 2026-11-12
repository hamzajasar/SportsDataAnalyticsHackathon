// Owner: Colleague A (Energy). Next: monthly chart from POST /api/club/energy (heating by month,
// solar for X kWp, net kWh, cost, CO2) for the club from useClub().requestClub.
import { useElectricityMix } from '@/api/queries'
import { TabTodo } from '@/components/club/TabTodo'
import { StatCard } from '@/components/common/StatCard'
import { ElectricityCard } from '@/components/footprint/ElectricityCard'
import { GridChartCard } from '@/components/footprint/GridChartCard'
import { useGridRows } from '@/hooks/use-footprint'
import { formatNumber } from '@/lib/format'
import { useClub } from '@/state/club'

export function EnergyTab() {
  const { club } = useClub()
  const { grid, latest, bih, eu } = useGridRows()
  const mix = useElectricityMix('BIH')
  const clubKwh = club
    ? club.electricity_kwh_year.floodlights +
      club.electricity_kwh_year.heating +
      club.electricity_kwh_year.hall_and_other
    : 20000
  return (
    <div className="space-y-4">
      <TabTodo>monthly energy profile + solar from POST /api/club/energy (Colleague A).</TabTodo>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
        <StatCard
          label={`BiH grid, ${latest?.year ?? ''}`}
          value={bih ? `${formatNumber(bih)} g/kWh` : '–'}
          hint="CO₂ per kWh of electricity"
          loading={grid.isLoading}
        />
        <StatCard
          label="vs EU average"
          value={bih && eu ? `${(bih / eu).toFixed(1)}×` : '–'}
          hint="dirtier electricity"
          loading={grid.isLoading}
        />
        <StatCard
          label={`Coal share, ${mix.data?.year ?? ''}`}
          value={mix.data ? `${formatNumber(mix.data.shares_pct.coal ?? 0)}%` : '–'}
          hint="of BiH electricity"
          loading={mix.isLoading}
        />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <GridChartCard />
        <ElectricityCard key={clubKwh} initialKwh={clubKwh} />
      </div>
    </div>
  )
}
