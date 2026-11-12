import { useSources, useAssumptions } from '@/api/queries'
import { useT } from '@/i18n'
import { QueryState } from '@/components/common/QueryState'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function SourcesPage() {
  const sources = useSources()
  const assumptions = useAssumptions()
  const a = assumptions.data
  const { t } = useT()

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">{t('sources.title')}</h2>
        <p className="text-sm text-muted-foreground">{t('sources.desc')}</p>
      </div>

      {/* Sources table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">{t('sources.dataTitle')}</CardTitle>
          <CardDescription>{t('sources.dataDesc')}</CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={sources.isLoading}
            error={sources.error}
            isEmpty={(sources.data?.length ?? 0) === 0}
            empty={t('sources.noSources')}
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="pr-4 pb-2 font-medium">{t('sources.colSource')}</th>
                    <th className="pr-4 pb-2 font-medium">{t('sources.colUse')}</th>
                    <th className="pr-4 pb-2 font-medium">{t('sources.colLicence')}</th>
                    <th className="pb-2 font-medium">{t('sources.colCredit')}</th>
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
          <CardTitle className="text-sm font-medium">{t('sources.costTitle')}</CardTitle>
          <CardDescription>{t('sources.costDesc')}</CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={assumptions.isLoading}
            error={assumptions.error}
            isEmpty={(a?.costs.length ?? 0) === 0}
            empty={t('sources.noAssumptions')}
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="pr-4 pb-2 font-medium">{t('sources.colKey')}</th>
                    <th className="pr-4 pb-2 font-medium">{t('sources.colValue')}</th>
                    <th className="pr-4 pb-2 font-medium">{t('sources.colUnit')}</th>
                    <th className="pr-4 pb-2 font-medium">{t('sources.colSource')}</th>
                    <th className="pb-2 font-medium">{t('sources.colNote')}</th>
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
          <CardTitle className="text-sm font-medium">{t('sources.upgradeTitle')}</CardTitle>
          <CardDescription>{t('sources.upgradeDesc')}</CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isLoading={assumptions.isLoading}
            error={assumptions.error}
            isEmpty={(a?.upgrades.length ?? 0) === 0}
            empty={t('sources.noUpgrades')}
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="pr-4 pb-2 font-medium">{t('sources.colUpgrade')}</th>
                    <th className="pr-4 pb-2 font-medium">{t('sources.colCostBasis')}</th>
                    <th className="pr-4 pb-2 font-medium">{t('sources.colSavingBasis')}</th>
                    <th className="pb-2 font-medium">{t('sources.colNote')}</th>
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
