import { CartesianGrid, Line, LineChart, XAxis, YAxis } from 'recharts'
import { Zap } from 'lucide-react'
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
import { useGridRows } from '@/hooks/use-footprint'
import { COUNTRIES } from '@/lib/footprint'

const gridConfig = {
  BIH: { label: 'Bosnia and Herzegovina', color: 'var(--chart-1)' },
  HRV: { label: 'Croatia', color: 'var(--chart-2)' },
  SRB: { label: 'Serbia', color: 'var(--chart-3)' },
  EU: { label: 'EU average', color: 'var(--chart-4)' },
} satisfies ChartConfig

/** BiH vs HR / RS / EU electricity CO2 per kWh over time (Ember). */
export function GridChartCard() {
  const { grid, rows } = useGridRows()
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="size-4" /> How clean is the electricity?
        </CardTitle>
        <CardDescription>Grams of CO₂ per kWh, by year (Ember)</CardDescription>
      </CardHeader>
      <CardContent>
        <QueryState isLoading={grid.isLoading} error={grid.error}>
          <ChartContainer config={gridConfig} className="h-72 w-full">
            <LineChart data={rows} margin={{ left: 0, right: 12 }}>
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
  )
}
