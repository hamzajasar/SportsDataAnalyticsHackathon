import { NavLink, Outlet } from 'react-router-dom'
import { BookOpen, Bus, HandCoins, LayoutDashboard, MapPin, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

const tabs = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/energy', label: 'Energy', icon: Zap },
  { to: '/travel', label: 'Travel', icon: Bus },
  { to: '/share', label: 'Share', icon: MapPin },
  { to: '/affordability', label: 'Affordability', icon: HandCoins },
  { to: '/sources', label: 'Sources', icon: BookOpen },
]

/** Tab bar shared by all club pages; each tab is its own page file in pages/club/. */
export function ClubLayout() {
  return (
    <div className="space-y-6">
      <nav className="-mx-4 flex gap-1 overflow-x-auto border-b px-4" aria-label="Club sections">
        {tabs.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'flex shrink-0 items-center gap-1.5 border-b-2 px-3 py-2 text-sm text-muted-foreground hover:text-foreground',
                isActive ? 'border-primary text-foreground' : 'border-transparent',
              )
            }
          >
            <Icon className="size-4" />
            {label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  )
}
