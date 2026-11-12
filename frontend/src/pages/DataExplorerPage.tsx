import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Database, KeyRound } from 'lucide-react'
import { useDatasetPreview, useDatasets, useDatasetSummary } from '@/api/queries'
import type { components } from '@/api/schema'
import { DataTable, type Column, type SortState } from '@/components/common/DataTable'
import { PageHeader } from '@/components/common/PageHeader'
import { QueryState } from '@/components/common/QueryState'
import { StatCard } from '@/components/common/StatCard'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatBytes, formatNumber } from '@/lib/format'
import { cn } from '@/lib/utils'

type ColumnSummary = components['schemas']['ColumnSummary']
const PAGE_SIZE = 50

const summaryColumns: Column<ColumnSummary>[] = [
  {
    key: 'name',
    header: 'Column',
    value: (c) => c.name,
    cell: (c) => (
      <span className="inline-flex items-center gap-1.5 font-medium">
        {c.name}
        {c.likely_key && <KeyRound className="size-3 text-primary" aria-label="likely key" />}
      </span>
    ),
  },
  {
    key: 'type',
    header: 'Type',
    value: (c) => c.type,
    cell: (c) => <Badge variant="outline">{c.type}</Badge>,
  },
  {
    key: 'null_pct',
    header: 'Missing',
    align: 'right',
    value: (c) => c.null_pct,
    cell: (c) => (
      <span className={cn(c.null_pct > 20 && 'font-medium text-destructive')}>{c.null_pct}%</span>
    ),
  },
  { key: 'approx_unique', header: 'Distinct', align: 'right', value: (c) => c.approx_unique },
  { key: 'min', header: 'Min', value: (c) => c.min },
  { key: 'max', header: 'Max', value: (c) => c.max },
  { key: 'mean', header: 'Mean', align: 'right', value: (c) => c.mean },
]

export function DataExplorerPage() {
  const [params, setParams] = useSearchParams()
  const datasets = useDatasets()
  const selectedId = params.get('id') ?? datasets.data?.[0]?.id

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data explorer"
        description={
          <>
            Every file in <code>data/raw/</code>. Run <code>make profile</code> for a full report.
          </>
        }
      />
      <QueryState
        isLoading={datasets.isLoading}
        error={datasets.error}
        isEmpty={!datasets.data?.length}
        empty={
          <>
            No datasets yet. Drop CSV / Parquet / JSON / Excel files into <code>data/raw/</code> (or
            run <code>make sample-data</code>).
          </>
        }
      >
        <div className="grid gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
          <nav className="flex gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
            {datasets.data?.map((d) => (
              <button
                key={d.id}
                type="button"
                onClick={() => setParams({ id: d.id })}
                className={cn(
                  'flex shrink-0 items-start gap-2 rounded-md border px-3 py-2 text-left text-sm hover:bg-muted',
                  d.id === selectedId && 'border-primary/40 bg-muted',
                )}
              >
                <Database className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                <span className="min-w-0">
                  <span className="block truncate font-medium">{d.id}</span>
                  <span className="text-xs text-muted-foreground">
                    {d.format} · {formatBytes(d.size_bytes)}
                  </span>
                </span>
              </button>
            ))}
          </nav>
          {selectedId && <DatasetDetail key={selectedId} id={selectedId} />}
        </div>
      </QueryState>
    </div>
  )
}

function DatasetDetail({ id }: { id: string }) {
  const [page, setPage] = useState(0)
  const [sort, setSort] = useState<SortState>(null)
  const summary = useDatasetSummary(id)
  const preview = useDatasetPreview(id, {
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
    sort: sort?.key,
    desc: sort?.desc,
  })

  const cols = summary.data?.columns ?? []
  const avgMissing = cols.length ? cols.reduce((s, c) => s + c.null_pct, 0) / cols.length : 0
  const total = preview.data?.total_rows ?? 0
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const previewColumns: Column<unknown[]>[] = (preview.data?.columns ?? []).map((name, i) => ({
    key: name,
    header: name,
    value: (row) => row[i],
  }))

  return (
    <div className="min-w-0 space-y-4">
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <StatCard
          label="Rows"
          value={formatNumber(summary.data?.rows ?? 0)}
          loading={summary.isLoading}
        />
        <StatCard label="Columns" value={cols.length} loading={summary.isLoading} />
        <StatCard
          label="Avg missing"
          value={`${avgMissing.toFixed(1)}%`}
          loading={summary.isLoading}
        />
        <StatCard
          label="Likely keys"
          value={
            cols
              .filter((c) => c.likely_key)
              .map((c) => c.name)
              .join(', ') || '—'
          }
          loading={summary.isLoading}
        />
      </div>

      <Tabs defaultValue="preview">
        <TabsList>
          <TabsTrigger value="preview">Rows</TabsTrigger>
          <TabsTrigger value="columns">Columns</TabsTrigger>
        </TabsList>

        <TabsContent value="preview">
          <Card>
            <CardContent className="space-y-3">
              <QueryState isLoading={preview.isLoading} error={preview.error}>
                <DataTable
                  columns={previewColumns}
                  rows={preview.data?.rows ?? []}
                  sort={sort}
                  onSortChange={(s) => {
                    setSort(s)
                    setPage(0)
                  }}
                  className={cn(preview.isFetching && 'opacity-60')}
                />
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    {formatNumber(total)} rows · page {page + 1} of {formatNumber(pages)}
                  </span>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page === 0}
                      onClick={() => setPage((p) => p - 1)}
                    >
                      <ChevronLeft /> Prev
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page + 1 >= pages}
                      onClick={() => setPage((p) => p + 1)}
                    >
                      Next <ChevronRight />
                    </Button>
                  </div>
                </div>
              </QueryState>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="columns">
          <Card>
            <CardContent>
              <QueryState isLoading={summary.isLoading} error={summary.error}>
                <DataTable columns={summaryColumns} rows={cols} rowKey={(c) => c.name} />
              </QueryState>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
