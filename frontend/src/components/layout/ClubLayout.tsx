import { NavLink, Outlet } from 'react-router-dom'
import { BarChart2, Bus, Euro, Leaf, MapPin, Printer, Share2 } from 'lucide-react'
import { cn } from '@/lib/utils'

const tabs = [
  { to: '/', label: 'Overview', icon: Leaf, end: true },
  { to: '/energy', label: 'Energy', icon: BarChart2, end: false },
  { to: '/travel', label: 'Travel', icon: Bus, end: false },
  { to: '/share', label: 'Share', icon: Share2, end: false },
  { to: '/affordability', label: 'Affordability', icon: Euro, end: false },
  { to: '/sources', label: 'Sources', icon: MapPin, end: false },
  { to: '/board-report', label: 'Board report', icon: Printer, end: false },
]

export function ClubLayout() {
  return (
    <div className="space-y-6">
      <nav className="no-print -mx-4 overflow-x-auto border-b px-4">
        <div className="flex gap-1 pb-0">
          {tabs.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  'flex shrink-0 items-center gap-1.5 border-b-2 px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:text-foreground',
                  isActive
                    ? 'border-primary text-foreground'
                    : 'border-transparent hover:border-muted',
                )
              }
            >
              <Icon className="size-3.5" />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
      <Outlet />
    </div>
  )
}
