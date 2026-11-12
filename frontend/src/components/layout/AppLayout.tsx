import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { Activity, Database, Info, LayoutDashboard, Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useHealth } from '@/api/queries'
import { project } from '@/content/project'
import { useTheme } from '@/hooks/use-theme'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import { cn } from '@/lib/utils'

const nav = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/data', label: 'Data', icon: Database },
  { to: '/methodology', label: 'How it works', icon: Info },
]

export function AppLayout() {
  const { theme, toggle } = useTheme()
  const health = useHealth()
  const location = useLocation()

  return (
    <div className="min-h-svh bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
          <div className="flex items-center gap-2 font-semibold">
            <Activity className="size-5" />
            <span>{project.name}</span>
          </div>
          <nav className="flex items-center gap-1">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground',
                    isActive && 'bg-muted text-foreground',
                  )
                }
              >
                <Icon className="size-4" />
                <span className="hidden sm:inline">{label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <Badge variant={health.data?.status === 'ok' ? 'secondary' : 'destructive'}>
              API {health.isLoading ? '…' : health.data?.status === 'ok' ? 'online' : 'offline'}
            </Badge>
            <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
              {theme === 'dark' ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <ErrorBoundary key={location.pathname}>
          <Outlet />
        </ErrorBoundary>
      </main>
    </div>
  )
}
