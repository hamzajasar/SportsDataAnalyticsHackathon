import type { ReactNode } from 'react'
import { AlertCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { errorMessage } from '@/lib/errors'
import { useT } from '@/i18n'

export function QueryState({
  isLoading,
  error,
  isEmpty,
  empty,
  children,
}: {
  isLoading: boolean
  error: unknown
  isEmpty?: boolean
  empty?: ReactNode
  children: ReactNode
}) {
  const { t } = useT()

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-2/3" />
      </div>
    )
  }
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle />
        <AlertTitle>{t('common.error')}</AlertTitle>
        <AlertDescription>{errorMessage(error)}</AlertDescription>
      </Alert>
    )
  }
  if (isEmpty) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        {empty ?? t('common.noData')}
      </p>
    )
  }
  return <>{children}</>
}
