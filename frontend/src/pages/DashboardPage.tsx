import { CartesianGrid, Line, LineChart, XAxis, YAxis } from 'recharts'
import { useSampleStats } from '@/api/queries'
import { EChart } from '@/components/charts/EChart'
import { PageHeader } from '@/components/common/PageHeader'
import { QueryState } from '@/components/common/QueryState'
import { StatCard } from '@/components/common/StatCard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'

const chartConfig = { value: { label: 'Value', color: 'var(--chart-1)' } } satisfies ChartConfig

export function DashboardPage() {
  const { data, isLoading, error } = useSampleStats()

  const points = data?.points ?? []
  const values = points.map((p) => p.value)
  const avg = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0

  const kpis = [
    { label: 'Data points', value: points.length },
    { label: 'Average', value: avg.toFixed(1) },
    { label: 'Max', value: values.length ? Math.max(...values).toFixed(1) : '–' },
    { label: 'Min', value: values.length ? Math.min(...values).toFixed(1) : '–' },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Placeholder page wired end-to-end (FastAPI → generated client → React Query → charts)."
      />

      <QueryState isLoading={false} error={error}>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {kpis.map((k) => (
            <StatCard key={k.label} label={k.label} value={k.value} loading={isLoading} />
          ))}
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>{data?.title ?? 'Loading…'}</CardTitle>
              <CardDescription>Recharts via shadcn/ui chart</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-72 w-full">
                <LineChart data={points} margin={{ left: 0, right: 12 }}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} width={32} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line dataKey="value" stroke="var(--color-value)" strokeWidth={2} dot={false} />
                </LineChart>
              </ChartContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Same data, ECharts</CardTitle>
              <CardDescription>Use for heatmaps, pitch/court maps, large data</CardDescription>
            </CardHeader>
            <CardContent>
              <EChart
                height={288}
                option={{
                  tooltip: { trigger: 'axis' },
                  grid: { left: 32, right: 12, top: 12, bottom: 24 },
                  xAxis: { type: 'category', data: points.map((p) => p.label) },
                  yAxis: { type: 'value' },
                  series: [
                    { type: 'bar', data: values, itemStyle: { borderRadius: [4, 4, 0, 0] } },
                  ],
                }}
              />
            </CardContent>
          </Card>
        </div>
      </QueryState>
    </div>
  )
}
