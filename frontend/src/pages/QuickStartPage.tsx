import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/api/client'
import { useCities } from '@/api/queries'
import { useClub } from '@/state/club'
import { useT, type Dict } from '@/i18n'
import type { components } from '@/api/schema'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Loader2 } from 'lucide-react'

type QuickClubInput = components['schemas']['QuickClubInput']

export function QuickStartPage() {
  const navigate = useNavigate()
  const { setClub } = useClub()
  const cities = useCities()
  const { t } = useT()

  const [city, setCity] = useState('')
  const [children, setChildren] = useState('60')
  const [teams, setTeams] = useState('4')
  const [paysElectricity, setPaysElectricity] = useState<'yes' | 'no'>('yes')
  const [monthlyBill, setMonthlyBill] = useState('')
  const [dontKnowBill, setDontKnowBill] = useState(false)
  const [heatingType, setHeatingType] = useState<QuickClubInput['heating_type']>('unknown')
  const [awayGames, setAwayGames] = useState('')
  const [avgKm, setAvgKm] = useState('')
  const [transport, setTransport] = useState<QuickClubInput['transport']>('mixed')

  const [submitting, setSubmitting] = useState(false)
  const [notes, setNotes] = useState<string[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const cityError = !city ? t('quick.cityRequired') : null
  const childrenError =
    !children || isNaN(parseInt(children)) || parseInt(children) < 1 ? t('quick.numberMin1') : null
  const teamsError =
    !teams || isNaN(parseInt(teams)) || parseInt(teams) < 1 ? t('quick.numberMin1') : null

  const canSubmit = !cityError && !childrenError && !teamsError

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!canSubmit) return
    setSubmitting(true)
    setError(null)
    try {
      const body: QuickClubInput = {
        city,
        children: parseInt(children),
        teams: parseInt(teams),
        pays_electricity: paysElectricity === 'yes',
        monthly_bill_km: dontKnowBill || !monthlyBill ? null : parseFloat(monthlyBill) || null,
        heating_type: heatingType,
        away_games_per_team: awayGames ? parseInt(awayGames) || null : null,
        avg_one_way_km: avgKm ? parseFloat(avgKm) || null : null,
        transport,
      }
      const { data, error: apiError } = await api.POST('/api/club/quick', { body })
      if (apiError) throw new Error(String(apiError))
      if (!data) throw new Error('No data returned')
      setClub(data.club)
      setNotes(data.notes)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('common.error'))
    } finally {
      setSubmitting(false)
    }
  }

  if (notes !== null) {
    return (
      <div className="mx-auto max-w-xl space-y-6">
        <div>
          <h1 className="text-xl font-semibold">{t('quick.ready')}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{t('quick.readyDesc')}</p>
        </div>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">{t('quick.assumed')}</CardTitle>
            <CardDescription>{t('quick.assumedDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1.5">
              {notes.map((note, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="mt-1 size-1.5 shrink-0 rounded-full bg-primary" />
                  {note}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-3">
          <Button onClick={() => navigate('/')}>{t('quick.viewOverview')}</Button>
          <Button variant="outline" onClick={() => navigate('/')}>
            {t('quick.editNumbers')}
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">{t('quick.title')}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{t('quick.desc')}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Location */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">{t('quick.location')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="city">{t('quick.cityLabel')}</Label>
              <Select value={city} onValueChange={(v) => setCity(v ?? '')}>
                <SelectTrigger id="city">
                  <SelectValue placeholder={t('quick.cityPlaceholder')} />
                </SelectTrigger>
                <SelectContent>
                  {cities.isLoading && (
                    <SelectItem value="__loading" disabled>
                      {t('quick.cityLoading')}
                    </SelectItem>
                  )}
                  {cities.data?.map((c) => (
                    <SelectItem key={c.city} value={c.city}>
                      {c.city}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Club size */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">{t('quick.size')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="children">{t('quick.children')}</Label>
                <Input
                  id="children"
                  type="number"
                  min="1"
                  value={children}
                  onChange={(e) => setChildren(e.target.value)}
                  placeholder="60"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="teams">{t('quick.teams')}</Label>
                <Input
                  id="teams"
                  type="number"
                  min="1"
                  value={teams}
                  onChange={(e) => setTeams(e.target.value)}
                  placeholder="4"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Energy */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">{t('quick.energy')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label>{t('quick.whoPaysBill')}</Label>
              <div className="flex gap-2">
                {(['yes', 'no'] as const).map((v) => (
                  <Button
                    key={v}
                    type="button"
                    variant={paysElectricity === v ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPaysElectricity(v)}
                  >
                    {v === 'yes' ? t('quick.ourClub') : t('quick.municipality')}
                  </Button>
                ))}
              </div>
            </div>

            {paysElectricity === 'yes' && (
              <div className="space-y-1.5">
                <Label htmlFor="bill">{t('quick.monthlyBill')}</Label>
                <div className="flex gap-2">
                  <Input
                    id="bill"
                    type="number"
                    min="0"
                    step="10"
                    value={dontKnowBill ? '' : monthlyBill}
                    onChange={(e) => {
                      setMonthlyBill(e.target.value)
                      setDontKnowBill(false)
                    }}
                    disabled={dontKnowBill}
                    placeholder="e.g. 150"
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant={dontKnowBill ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setDontKnowBill((v) => !v)}
                  >
                    {t('quick.dontKnow')}
                  </Button>
                </div>
              </div>
            )}

            <div className="space-y-1.5">
              <Label htmlFor="heating">{t('quick.heatingType')}</Label>
              <Select
                value={heatingType}
                onValueChange={(v) =>
                  setHeatingType((v ?? 'unknown') as QuickClubInput['heating_type'])
                }
              >
                <SelectTrigger id="heating">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(
                    [
                      'electric',
                      'district',
                      'gas',
                      'wood',
                      'other',
                      'unknown',
                    ] as QuickClubInput['heating_type'][]
                  ).map((k) => (
                    <SelectItem key={k} value={k}>
                      {t(`heating.${k}` as keyof Dict)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Travel */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">{t('quick.awayTravel')}</CardTitle>
            <CardDescription>{t('quick.awayTravelDesc')}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="away-games">{t('quick.awayGames')}</Label>
                <Input
                  id="away-games"
                  type="number"
                  min="0"
                  value={awayGames}
                  onChange={(e) => setAwayGames(e.target.value)}
                  placeholder="e.g. 10"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="avg-km">{t('quick.avgKm')}</Label>
                <Input
                  id="avg-km"
                  type="number"
                  min="0"
                  step="5"
                  value={avgKm}
                  onChange={(e) => setAvgKm(e.target.value)}
                  placeholder="e.g. 30"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label>{t('quick.transport')}</Label>
              <div className="flex flex-wrap gap-2">
                {(['cars', 'minibus', 'mixed'] as QuickClubInput['transport'][]).map((k) => (
                  <Button
                    key={k}
                    type="button"
                    variant={transport === k ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTransport(k)}
                  >
                    {t(`transport.${k}` as keyof Dict)}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={!canSubmit || submitting}>
            {submitting && <Loader2 className="mr-2 size-4 animate-spin" />}
            {t('quick.submit')}
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate('/')}>
            {t('quick.useExample')}
          </Button>
        </div>

        {!canSubmit && (
          <div className="flex flex-wrap gap-2">
            {cityError && <Badge variant="destructive">{cityError}</Badge>}
            {childrenError && <Badge variant="destructive">{childrenError}</Badge>}
            {teamsError && <Badge variant="destructive">{teamsError}</Badge>}
          </div>
        )}
      </form>
    </div>
  )
}
