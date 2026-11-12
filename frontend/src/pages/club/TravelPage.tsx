import { useState } from 'react'
import { Bus, Car, TrainFront } from 'lucide-react'
import { useClub } from '@/state/club'
import { useSeasonTravel } from '@/api/queries'
import { useT } from '@/i18n'
import { QueryState } from '@/components/common/QueryState'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { formatNumber } from '@/lib/format'
import { cn } from '@/lib/utils'

const MODE_ICON: Record<string, typeof Car> = {
  cars: Car,
  minibus: Bus,
  coach: Bus,
  rail: TrainFront,
  current: Car,
}

export function TravelPage() {
  const { club } = useClub()
  const [people, setPeople] = useState(18)
  const [share, setShare] = useState(false)
  const { t } = useT()

  const season = useSeasonTravel(club, people, share)
  const st = season.data

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">{t('travel.title')}</h2>
        <p className="text-sm text-muted-foreground">{t('travel.desc')}</p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-end gap-4">
        <div className="grid gap-1.5">
          <Label htmlFor="people">{t('travel.people')}</Label>
          <Input
            id="people"
            type="number"
            inputMode="decimal"
            min={1}
            value={people}
            className="w-28"
            onChange={(e) => setPeople(Math.max(1, Number(e.target.value) || 1))}
          />
        </div>
        <Button
          variant={share ? 'default' : 'outline'}
          onClick={() => setShare((s) => !s)}
          className="mb-0.5"
        >
          {share ? t('travel.sharingCoach') : t('travel.shareCoach')}
        </Button>
      </div>

      {st && (
        <p className="text-sm text-muted-foreground">
          {st.trips} × {formatNumber(st.round_trip_km)} km · {st.people_per_trip} pax
          {st.share_with_partner && st.shared_with.length > 0
            ? ` · ${t('travel.sharingWith', { clubs: st.shared_with.join(', ') })}`
            : ''}
          {st.note && ` · ${st.note}`}
        </p>
      )}

      {/* Season options */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">{t('travel.seasonTitle')}</CardTitle>
          <CardDescription>{t('travel.seasonDesc')}</CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState isLoading={season.isLoading} error={season.error}>
            <div className="space-y-3">
              {(st?.options ?? []).map((opt) => {
                const Icon = MODE_ICON[opt.mode] ?? Bus
                const isCheapest = opt.mode === st?.cheapest
                const isLowCo2 = opt.mode === st?.lowest_co2
                return (
                  <div
                    key={opt.mode}
                    className={cn(
                      'rounded-lg border p-3',
                      (isCheapest || isLowCo2) && 'border-primary/40 bg-primary/5',
                    )}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Icon className="size-4 text-muted-foreground" />
                        <span className="font-medium">{opt.label}</span>
                        {isCheapest && <Badge variant="default">{t('travel.cheapest')}</Badge>}
                        {isLowCo2 && <Badge variant="secondary">{t('travel.lowestCo2')}</Badge>}
                      </div>
                      <div className="flex items-center gap-4 text-sm tabular-nums">
                        <span>{formatNumber(opt.cost_km)} KM</span>
                        <span>{(opt.co2_kg / 1000).toFixed(1)} t CO₂</span>
                      </div>
                    </div>
                    {opt.mode !== 'current' && (
                      <div className="mt-1.5 flex gap-4 text-xs text-muted-foreground">
                        {opt.saving_vs_current_cost_km > 0 && (
                          <span>
                            {t('travel.savesKm', {
                              km: formatNumber(opt.saving_vs_current_cost_km),
                            })}
                          </span>
                        )}
                        {opt.saving_vs_current_co2_kg > 0 && (
                          <span>
                            {t('travel.savesCo2', {
                              t: (opt.saving_vs_current_co2_kg / 1000).toFixed(1),
                            })}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </QueryState>
        </CardContent>
      </Card>
    </div>
  )
}
