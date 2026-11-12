import { Link, Outlet, useLocation } from 'react-router-dom'
import { Activity, Info, Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useHealth } from '@/api/queries'
import { project } from '@/content/project'
import { useTheme } from '@/hooks/use-theme'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import { useT, type Lang } from '@/i18n'

export function AppLayout() {
  const { theme, toggle } = useTheme()
  const health = useHealth()
  const location = useLocation()
  const { t, lang, setLang } = useT()

  const apiLabel = health.isLoading
    ? t('nav.apiLoading')
    : health.data?.status === 'ok'
      ? t('nav.apiOnline')
      : t('nav.apiOffline')

  return (
    <div className="min-h-svh bg-background text-foreground">
      <header className="no-print sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4">
          <Link to="/" className="flex items-center gap-2 font-semibold hover:opacity-80">
            <Activity className="size-5" />
            <span className="hidden sm:inline">{project.name}</span>
          </Link>
          <nav className="flex items-center gap-1">
            <Link
              to="/methodology"
              className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground"
            >
              <Info className="size-4" />
              <span className="hidden sm:inline">{t('nav.howItWorks')}</span>
            </Link>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <Badge variant={health.data?.status === 'ok' ? 'secondary' : 'destructive'}>
              {apiLabel}
            </Badge>
            {/* Language switcher */}
            <div
              className="no-print flex overflow-hidden rounded-md border"
              role="group"
              aria-label={t('nav.langSwitch')}
            >
              {(['en', 'bs'] as Lang[]).map((l) => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  aria-pressed={lang === l}
                  className={`px-2.5 py-1 text-xs font-medium transition-colors ${
                    lang === l
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {l.toUpperCase()}
                </button>
              ))}
            </div>
            <Button variant="ghost" size="icon" onClick={toggle} aria-label={t('nav.toggleTheme')}>
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
