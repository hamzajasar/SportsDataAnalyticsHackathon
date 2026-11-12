// Owner: Colleague B (Travel). Next: season view from POST /api/club/travel (all away trips:
// KM cost + CO2 per option, coach shared with a partner club) for useClub().requestClub.
import { TabTodo } from '@/components/club/TabTodo'
import { TripCard } from '@/components/footprint/TripCard'

export function TravelTab() {
  return (
    <div className="space-y-4">
      <TabTodo>season travel cost + CO₂ from POST /api/club/travel (Colleague B).</TabTodo>
      <div className="grid gap-4 lg:grid-cols-2">
        <TripCard />
      </div>
    </div>
  )
}
