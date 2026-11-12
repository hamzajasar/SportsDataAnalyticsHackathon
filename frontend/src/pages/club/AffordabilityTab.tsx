// Owner: Colleague A (Affordability). Next: POST /api/club/affordability — cost per child today,
// fee drop per action, cost per child after — for useClub().requestClub.
import { TabTodo } from '@/components/club/TabTodo'
import { KitCard } from '@/components/footprint/KitCard'

export function AffordabilityTab() {
  return (
    <div className="space-y-4">
      <TabTodo>
        cost per child before/after from POST /api/club/affordability (Colleague A).
      </TabTodo>
      <div className="grid gap-4 lg:grid-cols-2">
        <KitCard />
      </div>
    </div>
  )
}
