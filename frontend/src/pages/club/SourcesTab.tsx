// Owner: you. Every data source with licence + the credit line for the final slide.
import { ExternalLink } from 'lucide-react'
import { useSources } from '@/api/queries'
import { DataTable, type Column } from '@/components/common/DataTable'
import { QueryState } from '@/components/common/QueryState'
import type { components } from '@/api/schema'

type Source = components['schemas']['Source']

const columns: Column<Source>[] = [
  {
    key: 'name',
    header: 'Source',
    value: (s) => s.name,
    cell: (s) =>
      s.url ? (
        <a
          href={s.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 underline"
        >
          {s.name} <ExternalLink className="size-3" />
        </a>
      ) : (
        s.name
      ),
  },
  { key: 'use', header: 'Used for', value: (s) => s.use },
  { key: 'licence', header: 'Licence', value: (s) => s.licence },
  { key: 'credit', header: 'Credit', value: (s) => s.credit },
]

export function SourcesTab() {
  const sources = useSources()
  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        Every number in this app comes from one of these sources. Prices marked as assumptions are
        estimates — check them for your own club.
      </p>
      <QueryState
        isLoading={sources.isLoading}
        error={sources.error}
        isEmpty={!sources.data?.length}
      >
        <DataTable columns={columns} rows={sources.data ?? []} rowKey={(s) => s.id} />
      </QueryState>
    </div>
  )
}
