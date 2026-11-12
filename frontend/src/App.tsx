import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ClubLayout } from '@/components/club/ClubLayout'
import { AppLayout } from '@/components/layout/AppLayout'
import { Skeleton } from '@/components/ui/skeleton'

// Each page is its own chunk: the first load only downloads the page you open.
const EnergyTab = lazy(() =>
  import('@/pages/club/EnergyTab').then((m) => ({ default: m.EnergyTab })),
)
const TravelTab = lazy(() =>
  import('@/pages/club/TravelTab').then((m) => ({ default: m.TravelTab })),
)
const ShareTab = lazy(() => import('@/pages/club/ShareTab').then((m) => ({ default: m.ShareTab })))
const AffordabilityTab = lazy(() =>
  import('@/pages/club/AffordabilityTab').then((m) => ({ default: m.AffordabilityTab })),
)
const SourcesTab = lazy(() =>
  import('@/pages/club/SourcesTab').then((m) => ({ default: m.SourcesTab })),
)
const OverviewPage = lazy(() =>
  import('@/pages/OverviewPage').then((m) => ({ default: m.OverviewPage })),
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
            <Route element={<ClubLayout />}>
              <Route index element={<OverviewPage />} />
              <Route path="energy" element={<EnergyTab />} />
              <Route path="travel" element={<TravelTab />} />
              <Route path="share" element={<ShareTab />} />
              <Route path="affordability" element={<AffordabilityTab />} />
              <Route path="sources" element={<SourcesTab />} />
            </Route>
            <Route path="data" element={<DataExplorerPage />} />
            <Route path="methodology" element={<MethodologyPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
