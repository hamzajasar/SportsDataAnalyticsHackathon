import { NavLink, Outlet } from 'react-router-dom'
import { BarChart2, Bus, Euro, Leaf, MapPin, Printer, ReceiptText, Share2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useT } from '@/i18n'
import type { en } from '@/i18n/en'

type TabDef = {
  to: string
  key: keyof typeof en
  icon: typeof Leaf
  end: boolean
}

const TAB_DEFS: TabDef[] = [
  { to: '/', key: 'tab.overview', icon: Leaf, end: true },
  { to: '/energy', key: 'tab.energy', icon: BarChart2, end: false },
  { to: '/travel', key: 'tab.travel', icon: Bus, end: false },
  { to: '/share', key: 'tab.share', icon: Share2, end: false },
  { to: '/affordability', key: 'tab.affordability', icon: Euro, end: false },
  { to: '/sources', key: 'tab.sources', icon: MapPin, end: false },
  { to: '/bill', key: 'tab.bill', icon: ReceiptText, end: false },
  { to: '/board-report', key: 'tab.boardReport', icon: Printer, end: false },
]

export function ClubLayout() {
  const { t } = useT()
  return (
    <div className="space-y-6">
      <nav className="no-print -mx-4 overflow-x-auto border-b px-4">
        <div className="flex gap-1 pb-0">
          {TAB_DEFS.map(({ to, key, icon: Icon, end }) => (
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
              <span>{t(key)}</span>
            </NavLink>
          ))}
        </div>
      </nav>
      <Outlet />
    </div>
  )
}
