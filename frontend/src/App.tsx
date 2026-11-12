import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { Skeleton } from '@/components/ui/skeleton'

// Each page is its own chunk: the first load only downloads the page you open.
const OverviewPage = lazy(() =>
  import('@/pages/OverviewPage').then((m) => ({ default: m.OverviewPage })),
)
const FootprintPage = lazy(() =>
  import('@/pages/FootprintPage').then((m) => ({ default: m.FootprintPage })),
)
const DataExplorerPage = lazy(() =>
  import('@/pages/DataExplorerPage').then((m) => ({ default: m.DataExplorerPage })),
)
const MethodologyPage = lazy(() =>
  import('@/pages/MethodologyPage').then((m) => ({ default: m.MethodologyPage })),
)
const NotFoundPage = lazy(() =>
  import('@/pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage })),
)

function PageFallback() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-72 w-full" />
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageFallback />}>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<OverviewPage />} />
            <Route path="footprint" element={<FootprintPage />} />
            <Route path="data" element={<DataExplorerPage />} />
            <Route path="methodology" element={<MethodologyPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
