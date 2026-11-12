import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'

// Use ECharts for heavy/custom visuals (heatmaps, pitch/court maps, large series).
// For simple bar/line charts prefer shadcn's <ChartContainer> (Recharts) in components/ui/chart.tsx.
export function EChart({ option, height = 320 }: { option: EChartsOption; height?: number }) {
  return (
    <ReactECharts
      option={{ backgroundColor: 'transparent', ...option }}
      style={{ height, width: '100%' }}
      notMerge
      lazyUpdate
    />
  )
}
