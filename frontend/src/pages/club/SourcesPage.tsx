import { useSources, useAssumptions } from '@/api/queries'
import { QueryState } from '@/components/common/QueryState'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function SourcesPage() {
  const sources = useSources()
  const assumptions = useAssumptions()
  const a = assumptions.data

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Sources & assumptions</h2>
        <p className="text-sm text-muted-foreground">
          Every number has a source. These credits also go on the final presentation slide.
        </p>
      </div>

      {/* Sources table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Data sources</CardTitle>
          <CardDescription>Licence and credit line for each dataset</CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={sources.isLoading}
            error={sources.error}
            isEmpty={(sources.data?.length ?? 0) === 0}
            empty="No sources loaded."
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="pr-4 pb-2 font-medium">Source</th>
                    <th className="pr-4 pb-2 font-medium">Use</th>
                    <th className="pr-4 pb-2 font-medium">Licence</th>
                    <th className="pb-2 font-medium">Credit</th>
                  </tr>
                </thead>
                <tbody>
                  {sources.data?.map((s) => (
                    <tr key={s.id} className="border-b last:border-0">
                      <td className="py-2 pr-4 align-top">
                        {s.url ? (
                          <a
                            href={s.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary underline-offset-2 hover:underline"
                          >
                            {s.name}
                          </a>
                        ) : (
                          s.name
                        )}
                      </td>
                      <td className="py-2 pr-4 align-top text-muted-foreground">{s.use ?? '—'}</td>
                      <td className="py-2 pr-4 align-top">
                        {s.licence ? (
                          <Badge variant="outline">{s.licence}</Badge>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="py-2 align-top text-muted-foreground">{s.credit ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </QueryState>
        </CardContent>
      </Card>

      {/* Cost assumptions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Cost assumptions</CardTitle>
          <CardDescription>
            Rows marked ASSUMPTION are estimates — not measured values
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={assumptions.isLoading}
            error={assumptions.error}
            isEmpty={(a?.costs.length ?? 0) === 0}
            empty="No assumptions loaded."
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="pr-4 pb-2 font-medium">Key</th>
                    <th className="pr-4 pb-2 font-medium">Value</th>
                    <th className="pr-4 pb-2 font-medium">Unit</th>
                    <th className="pr-4 pb-2 font-medium">Source</th>
                    <th className="pb-2 font-medium">Note</th>
                  </tr>
                </thead>
                <tbody>
                  {a?.costs.map((c) => {
                    const isAssumption = c.source.toUpperCase().includes('ASSUMPTION')
                    return (
                      <tr
                        key={c.key}
                        className={`border-b last:border-0 ${isAssumption ? 'bg-yellow-50/50 dark:bg-yellow-950/20' : ''}`}
                      >
                        <td className="py-2 pr-4 align-top font-mono text-xs">{c.key}</td>
                        <td className="py-2 pr-4 align-top tabular-nums">{c.value}</td>
                        <td className="py-2 pr-4 align-top text-muted-foreground">{c.unit}</td>
                        <td className="py-2 pr-4 align-top">
                          {isAssumption ? (
                            <Badge variant="secondary">ASSUMPTION</Badge>
                          ) : (
                            <span className="text-muted-foreground">{c.source}</span>
                          )}
                        </td>
                        <td className="py-2 align-top text-muted-foreground">{c.note ?? '—'}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </QueryState>
        </CardContent>
      </Card>

      {/* Upgrades */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Upgrade assumptions</CardTitle>
          <CardDescription>
            Cost and saving basis for each upgrade in the action plan
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={assumptions.isLoading}
            error={assumptions.error}
            isEmpty={(a?.upgrades.length ?? 0) === 0}
            empty="No upgrade data loaded."
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="pr-4 pb-2 font-medium">Upgrade</th>
                    <th className="pr-4 pb-2 font-medium">Cost basis</th>
                    <th className="pr-4 pb-2 font-medium">Saving basis</th>
                    <th className="pb-2 font-medium">Note</th>
                  </tr>
                </thead>
                <tbody>
                  {a?.upgrades.map((u) => (
                    <tr key={u.id} className="border-b last:border-0">
                      <td className="py-2 pr-4 align-top font-medium">{u.name}</td>
                      <td className="py-2 pr-4 align-top text-muted-foreground">
                        {u.kwp != null
                          ? `${u.kwp} kWp × ${u.cost_km_per_kwp ?? '—'} KM/kWp`
                          : `${u.cost_km ?? '—'} KM`}
                      </td>
                      <td className="py-2 pr-4 align-top text-muted-foreground">
                        {u.share != null ? `${(u.share * 100).toFixed(0)}%` : '—'}
                      </td>
                      <td className="py-2 align-top text-muted-foreground">{u.note ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </QueryState>
        </CardContent>
      </Card>
    </div>
  )
}
