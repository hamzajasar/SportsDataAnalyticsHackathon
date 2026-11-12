import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { useT } from '@/i18n'

class ErrorBoundaryInner extends Component<
  { children: ReactNode; fallback?: ReactNode; errorLabel: string; tryAgainLabel: string },
  { error: Error | null }
> {
  state = { error: null as Error | null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(error, info.componentStack)
  }

  render() {
    if (!this.state.error) return this.props.children
    return (
      this.props.fallback ?? (
        <div className="rounded-lg border border-destructive/40 p-6 text-sm">
          <p className="font-medium">{this.props.errorLabel}</p>
          <p className="mt-1 font-mono text-xs text-muted-foreground">{this.state.error.message}</p>
          <Button
            size="sm"
            variant="outline"
            className="mt-3"
            onClick={() => this.setState({ error: null })}
          >
            {this.props.tryAgainLabel}
          </Button>
        </div>
      )
    )
  }
}

export function ErrorBoundary({
  children,
  fallback,
}: {
  children: ReactNode
  fallback?: ReactNode
}) {
  const { t } = useT()
  return (
    <ErrorBoundaryInner
      errorLabel={t('common.failedRender')}
      tryAgainLabel={t('common.tryAgain')}
      fallback={fallback}
    >
      {children}
    </ErrorBoundaryInner>
  )
}
