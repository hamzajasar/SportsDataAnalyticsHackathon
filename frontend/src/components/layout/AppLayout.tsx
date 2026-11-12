import { Link, Outlet, useLocation } from 'react-router-dom'
import { Activity, Info, Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useHealth } from '@/api/queries'
import { project } from '@/content/project'
import { useTheme } from '@/hooks/use-theme'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'

const secondaryNav = [
  { to: '/methodology', label: 'How it works', icon: Info },
]

export function AppLayout() {
  const { theme, toggle } = useTheme()
  const health = useHealth()
  const location = useLocation()

  return (
    <div className="min-h-svh bg-background text-foreground">
      <header className="no-print sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
          <Link to="/" className="flex items-center gap-2 font-semibold hover:opacity-80">
            <Activity className="size-5" />
            <span className="hidden sm:inline">{project.name}</span>
          </Link>
          <nav className="flex items-center gap-1">
            {secondaryNav.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground"
              >
                <Icon className="size-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
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
