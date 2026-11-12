import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { ClubLayout } from '@/components/layout/ClubLayout'
import { Skeleton } from '@/components/ui/skeleton'

const OverviewPage = lazy(() =>
  import('@/pages/club/OverviewPage').then((m) => ({ default: m.OverviewPage })),
)
const EnergyPage = lazy(() =>
  import('@/pages/club/EnergyPage').then((m) => ({ default: m.EnergyPage })),
)
const TravelPage = lazy(() =>
  import('@/pages/club/TravelPage').then((m) => ({ default: m.TravelPage })),
)
const SharePage = lazy(() =>
  import('@/pages/club/SharePage').then((m) => ({ default: m.SharePage })),
)
const AffordabilityPage = lazy(() =>
  import('@/pages/club/AffordabilityPage').then((m) => ({ default: m.AffordabilityPage })),
)
const SourcesPage = lazy(() =>
  import('@/pages/club/SourcesPage').then((m) => ({ default: m.SourcesPage })),
)
const BillPage = lazy(() => import('@/pages/club/BillPage').then((m) => ({ default: m.BillPage })))
const BoardReportPage = lazy(() =>
  import('@/pages/BoardReportPage').then((m) => ({ default: m.BoardReportPage })),
)
const MethodologyPage = lazy(() =>
  import('@/pages/MethodologyPage').then((m) => ({ default: m.MethodologyPage })),
)
const QuickStartPage = lazy(() =>
  import('@/pages/QuickStartPage').then((m) => ({ default: m.QuickStartPage })),
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
              <Route path="energy" element={<EnergyPage />} />
              <Route path="travel" element={<TravelPage />} />
              <Route path="share" element={<SharePage />} />
              <Route path="affordability" element={<AffordabilityPage />} />
              <Route path="sources" element={<SourcesPage />} />
              <Route path="bill" element={<BillPage />} />
              <Route path="board-report" element={<BoardReportPage />} />
            </Route>
            <Route path="quick-start" element={<QuickStartPage />} />
            <Route path="methodology" element={<MethodologyPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
