import { useState } from 'react'
import { Copy, Printer, ReceiptText } from 'lucide-react'
import { useClub } from '@/state/club'
import { useAnalyseBill, type BillAnalysis, type ConfirmedBill } from '@/api/bill'
import { useT } from '@/i18n'
import { QueryState } from '@/components/common/QueryState'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { formatNumber, monthName } from '@/lib/format'
import { cn } from '@/lib/utils'

const MONTH_INDICES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

type StatusKey = 'normal' | 'above' | 'high' | 'below' | 'unknown'
const STATUS_VARIANT: Record<StatusKey, 'secondary' | 'outline' | 'destructive'> = {
  normal: 'secondary',
  above: 'outline',
  high: 'destructive',
  below: 'secondary',
  unknown: 'outline',
}

const SAMPLE = { month: 1, year: 2026, kwh: '9420', amount: '2900' }
const selectClass =
  'h-9 rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring'

function num(s: string): number | null {
  const n = Number(s.replace(',', '.'))
  return s.trim() !== '' && Number.isFinite(n) && n > 0 ? n : null
}

function signed(n: number, digits = 0) {
  return `${n > 0 ? '+' : n < 0 ? '−' : ''}${formatNumber(Math.abs(n), digits)}`
}

export function BillPage() {
  const { club } = useClub()
  const { t } = useT()
  const [kind, setKind] = useState<'electricity' | 'fuel'>('electricity')
  const [month, setMonth] = useState(() => new Date().getMonth() + 1)
  const [year, setYear] = useState(() => String(new Date().getFullYear()))
  const [kwh, setKwh] = useState('')
  const [amount, setAmount] = useState('')
  const [temp, setTemp] = useState('')
  const [fuelType, setFuelType] = useState<'diesel' | 'petrol'>('diesel')
  const [litres, setLitres] = useState('')
  const [submitted, setSubmitted] = useState<{ bill: ConfirmedBill; temp: number | null } | null>(
    null,
  )
  const [copied, setCopied] = useState(false)

  const buildBill = (): ConfirmedBill | null => {
    if (kind === 'electricity') {
      const k = num(kwh)
      return k
        ? {
            kind,
            period_month: month,
            period_year: Number(year) || null,
            kwh: k,
            amount_km: num(amount),
          }
        : null
    }
    const l = num(litres)
    const a = num(amount)
    return l && a ? { kind, fuel_type: fuelType, litres: l, amount_km: a } : null
  }

  const bill = buildBill()
  const tempNum = temp.trim() === '' || !Number.isFinite(Number(temp)) ? null : Number(temp)
  const analysis = useAnalyseBill(club, submitted?.bill ?? null, submitted?.temp ?? null)
  const data = analysis.data

  const useSample = () => {
    setKind('electricity')
    setMonth(SAMPLE.month)
    setYear(String(SAMPLE.year))
    setKwh(SAMPLE.kwh)
    setAmount(SAMPLE.amount)
    setTemp('')
    setSubmitted({
      bill: {
        kind: 'electricity',
        period_month: SAMPLE.month,
        period_year: SAMPLE.year,
        kwh: Number(SAMPLE.kwh),
        amount_km: Number(SAMPLE.amount),
      },
      temp: null,
    })
  }

  const copyText = async () => {
    if (!data) return
    try {
      await navigator.clipboard.writeText(data.board_text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      /* clipboard unavailable */
    }
  }

  return (
    <div className="space-y-6">
      <div className="no-print">
        <h2 className="text-lg font-semibold">{t('bill.title')}</h2>
        <p className="text-sm text-muted-foreground">{t('bill.desc')}</p>
      </div>

      <Card className="no-print">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ReceiptText className="size-4" /> {t('bill.cardTitle')}
          </CardTitle>
          <CardDescription>{t('bill.cardDesc')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button
              variant={kind === 'electricity' ? 'default' : 'outline'}
              onClick={() => setKind('electricity')}
            >
              {t('bill.electricity')}
            </Button>
            <Button
              variant={kind === 'fuel' ? 'default' : 'outline'}
              onClick={() => setKind('fuel')}
            >
              {t('bill.fuel')}
            </Button>
          </div>

          <div className="flex flex-wrap items-end gap-4">
            {kind === 'electricity' ? (
              <>
                <div className="grid gap-1.5">
                  <Label htmlFor="bill-month">{t('bill.month')}</Label>
                  <select
                    id="bill-month"
                    className={selectClass}
                    value={month}
                    onChange={(e) => setMonth(Number(e.target.value))}
                  >
                    {MONTH_INDICES.map((i) => (
                      <option key={i} value={i + 1}>
                        {monthName(i, 'long')}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor="bill-year">{t('bill.year')}</Label>
                  <Input
                    id="bill-year"
                    type="number"
                    inputMode="numeric"
                    className="w-24"
                    value={year}
                    onChange={(e) => setYear(e.target.value)}
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor="bill-kwh">{t('bill.kwh')}</Label>
                  <Input
                    id="bill-kwh"
                    type="text"
                    inputMode="decimal"
                    className="w-36"
                    placeholder="e.g. 9420"
                    value={kwh}
                    onChange={(e) => setKwh(e.target.value)}
                  />
                </div>
              </>
            ) : (
              <>
                <div className="grid gap-1.5">
                  <Label htmlFor="bill-fuel">{t('bill.fuelType')}</Label>
                  <select
                    id="bill-fuel"
                    className={selectClass}
                    value={fuelType}
                    onChange={(e) => setFuelType(e.target.value as 'diesel' | 'petrol')}
                  >
                    <option value="diesel">Diesel</option>
                    <option value="petrol">Petrol</option>
                  </select>
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor="bill-litres">{t('bill.litres')}</Label>
                  <Input
                    id="bill-litres"
                    type="text"
                    inputMode="decimal"
                    className="w-28"
                    placeholder="e.g. 40"
                    value={litres}
                    onChange={(e) => setLitres(e.target.value)}
                  />
                </div>
              </>
            )}
            <div className="grid gap-1.5">
              <Label htmlFor="bill-amount">
                {kind === 'electricity' ? t('bill.amountOptional') : t('bill.amountRequired')}
              </Label>
              <Input
                id="bill-amount"
                type="text"
                inputMode="decimal"
                className="w-36"
                placeholder="e.g. 2900"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>
            {kind === 'electricity' && (
              <div className="grid gap-1.5">
                <Label htmlFor="bill-temp">{t('bill.tempLabel')}</Label>
                <Input
                  id="bill-temp"
                  type="text"
                  inputMode="decimal"
                  className="w-36"
                  placeholder={t('bill.tempPlaceholder')}
                  value={temp}
                  onChange={(e) => setTemp(e.target.value)}
                />
              </div>
            )}
          </div>

          <div className="flex flex-wrap gap-2">
            <Button disabled={!bill} onClick={() => bill && setSubmitted({ bill, temp: tempNum })}>
              {t('bill.checkBtn')}
            </Button>
            <Button variant="outline" onClick={useSample}>
              {t('bill.sampleBtn')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {submitted && (
        <QueryState isLoading={analysis.isLoading} error={analysis.error}>
          {data && <Results data={data} copied={copied} onCopy={copyText} />}
        </QueryState>
      )}
    </div>
  )
}

function Results({
  data,
  copied,
  onCopy,
}: {
  data: BillAnalysis
  copied: boolean
  onCopy: () => void
}) {
  const { t } = useT()
  const w = data.waste
  const f = data.fuel
  const { before, after } = data.plan
  const statusKey = (w?.status ?? 'unknown') as StatusKey
  const statusVariant = STATUS_VARIANT[statusKey] ?? 'outline'
  const pct = w?.difference_pct ?? null

  const statusLabel = (): string => {
    switch (statusKey) {
      case 'normal':
        return t('bill.statusNormal')
      case 'above':
        return t('bill.statusAbove')
      case 'high':
        return t('bill.statusHigh')
      case 'below':
        return t('bill.statusBelow')
      default:
        return t('bill.statusUnknown')
    }
  }

  const checkText = (s: string): string => {
    switch (s) {
      case 'floodlights':
        return t('bill.checkFloodlights')
      case 'heating':
        return t('bill.checkHeating')
      case 'baseload':
        return t('bill.checkBaseload')
      default:
        return s
    }
  }

  const rows: { label: string; b: number; a: number; unit: string; digits?: number }[] = [
    {
      label: t('bill.savePerYear'),
      b: before.total_saves_km_year,
      a: after.total_saves_km_year,
      unit: 'KM',
    },
    {
      label: t('bill.cutCo2'),
      b: before.total_saves_t_co2_year,
      a: after.total_saves_t_co2_year,
      unit: 't',
      digits: 1,
    },
    {
      label: t('bill.feeDrop'),
      b: before.fee_drop_per_child_km,
      a: after.fee_drop_per_child_km,
      unit: 'KM',
      digits: 1,
    },
  ]

  return (
    <div className="space-y-6">
      {data.illustrative_club && (
        <Badge variant="outline" className="no-print">
          {t('bill.illustrative')}
        </Badge>
      )}

      {data.warnings.length > 0 && (
        <Alert className="no-print">
          <AlertTitle>{t('bill.warnings')}</AlertTitle>
          <AlertDescription>
            <ul className="list-disc pl-4">
              {data.warnings.map((m) => (
                <li key={m}>{m}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {w && (
        <Card className="no-print">
          <CardHeader>
            <CardTitle className="flex flex-wrap items-center gap-2">
              {t('bill.weatherQuestion')}
              <Badge variant={statusVariant}>{statusLabel()}</Badge>
            </CardTitle>
            <CardDescription>{w.temperature_source}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex flex-wrap items-baseline gap-x-6 gap-y-1">
              {pct !== null && (
                <p
                  className={cn(
                    'text-3xl font-semibold tabular-nums',
                    w.status === 'high' && 'text-destructive',
                  )}
                >
                  {signed(pct, 1)} %
                </p>
              )}
              <p className="text-sm text-muted-foreground">
                {formatNumber(w.actual_kwh)} kWh billed vs {formatNumber(w.expected_kwh)} kWh
                expected at {w.temperature_c} °C
              </p>
            </div>
            {w.excess_km > 0 && (
              <p className="text-sm">
                About <strong>{formatNumber(w.excess_kwh)} kWh</strong> more than expected, roughly{' '}
                <strong>{formatNumber(w.excess_km)} KM</strong> extra this month.
              </p>
            )}
            {w.suggestions.length > 0 && (
              <div>
                <p className="mb-1 text-sm font-medium">{t('bill.checkFirst')}</p>
                <ul className="list-disc space-y-0.5 pl-5 text-sm text-muted-foreground">
                  {w.suggestions.map((s) => (
                    <li key={s}>{checkText(s)}</li>
                  ))}
                </ul>
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              {t('bill.flagNote')} {w.basis}.
            </p>
          </CardContent>
        </Card>
      )}

      {f && (
        <Card className="no-print">
          <CardHeader>
            <CardTitle>{t('bill.fuelTitle')}</CardTitle>
          </CardHeader>
          <CardContent className="text-sm">
            You paid <strong>{formatNumber(f.price_km_per_litre, 2)} KM/l</strong> for {f.fuel_type}
            ; the plan assumed {formatNumber(f.assumed_km_per_litre, 2)} KM/l (
            {signed(f.difference_pct, 1)} %). The travel costs below use your price.
          </CardContent>
        </Card>
      )}

      <Card className="no-print">
        <CardHeader>
          <CardTitle>{t('bill.planTitle')}</CardTitle>
          <CardDescription>{data.plan.based_on}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-3">
            {rows.map((r) => (
              <div key={r.label} className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">{r.label}</p>
                <p className="mt-1 text-2xl font-semibold tabular-nums">
                  {formatNumber(r.a, r.digits ?? 0)} {r.unit}
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  was {formatNumber(r.b, r.digits ?? 0)} · {signed(r.a - r.b, r.digits ?? 0)}
                </p>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground">
            Electricity price used: {formatNumber(data.plan.price_km_per_kwh_used, 3)} KM/kWh (
            {data.plan.price_source}).
            {data.plan.annual_kwh_estimate !== null &&
              data.plan.annual_kwh_estimate !== undefined &&
              ` Yearly electricity estimate: ${formatNumber(data.plan.annual_kwh_estimate)} kWh (was ${formatNumber(before.electricity_kwh_year)}).`}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="no-print">
          <CardTitle>{t('bill.boardTitle')}</CardTitle>
          <CardDescription>{t('bill.boardDesc')}</CardDescription>
          <div className="flex gap-2 pt-2">
            <Button onClick={() => window.print()}>
              <Printer className="size-4" /> {t('common.print')}
            </Button>
            <Button variant="outline" onClick={onCopy}>
              <Copy className="size-4" /> {copied ? t('common.copied') : t('common.copyText')}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <pre className="font-sans text-sm leading-relaxed whitespace-pre-wrap">
            {data.board_text}
          </pre>
        </CardContent>
      </Card>
    </div>
  )
}
