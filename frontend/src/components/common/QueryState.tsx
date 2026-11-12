import type { ReactNode } from 'react'
import { AlertCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { errorMessage } from '@/lib/errors'

/** Standard loading / error / empty handling for a React Query result. */
export function QueryState({
  isLoading,
  error,
  isEmpty,
  empty = 'No data.',
  children,
}: {
  isLoading: boolean
  error: unknown
  isEmpty?: boolean
  empty?: ReactNode
  children: ReactNode
}) {
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
        <AlertTitle>Something went wrong</AlertTitle>
        <AlertDescription>{errorMessage(error)}</AlertDescription>
      </Alert>
    )
  }
  if (isEmpty) return <p className="py-8 text-center text-sm text-muted-foreground">{empty}</p>
  return <>{children}</>
}
