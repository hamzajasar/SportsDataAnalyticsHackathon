// Owner: Colleague B (Share). Next: map of venues (add react-leaflet + OSM tiles in this branch).
import { MapPin, Users } from 'lucide-react'
import { useShareSuggestions } from '@/api/queries'
import { TabTodo } from '@/components/club/TabTodo'
import { QueryState } from '@/components/common/QueryState'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useClub } from '@/state/club'

type Venue = {
  id: string
  name?: string | null
  leisure?: string | null
  distance_km?: number | null
}

function VenueList({ items }: { items: Venue[] }) {
  if (!items.length) return <p className="text-sm text-muted-foreground">None within range.</p>
  return (
    <ul className="space-y-1.5 text-sm">
      {items.map((v) => (
        <li key={v.id} className="flex justify-between gap-2">
          <span className="truncate">{v.name ?? v.leisure?.replace('_', ' ')}</span>
          <span className="shrink-0 text-muted-foreground tabular-nums">{v.distance_km} km</span>
        </li>
      ))}
    </ul>
  )
}

export function ShareTab() {
  const { club } = useClub()
  const s = useShareSuggestions(club?.lat, club?.lon, 10)
  return (
    <div className="space-y-4">
      <TabTodo>map of BiH venues with react-leaflet (Colleague B).</TabTodo>
      <QueryState isLoading={s.isLoading} error={s.error}>
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="size-4" /> Pitches and halls to share
              </CardTitle>
              <CardDescription>
                Within {s.data?.radius_km} km — use instead of building or heating your own
              </CardDescription>
            </CardHeader>
            <CardContent>
              <VenueList items={s.data?.shared_pitch ?? []} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="size-4" /> Clubs nearby to share transport with
              </CardTitle>
              <CardDescription>{s.data?.note}</CardDescription>
            </CardHeader>
            <CardContent>
              <VenueList items={s.data?.carpool_partners ?? []} />
            </CardContent>
          </Card>
        </div>
      </QueryState>
      <p className="text-xs text-muted-foreground">© OpenStreetMap contributors (ODbL)</p>
    </div>
  )
}
