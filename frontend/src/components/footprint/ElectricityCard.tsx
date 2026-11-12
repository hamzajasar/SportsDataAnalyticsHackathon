import { useState } from 'react'
import { Zap } from 'lucide-react'
import { NumberField } from '@/components/common/NumberField'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useFactorMap, useGridRows } from '@/hooks/use-footprint'
import { formatNumber } from '@/lib/format'
import { carKm } from '@/lib/footprint'

/** kWh on the bill -> kg CO2 on the BiH grid vs the same use on the EU grid. */
export function ElectricityCard({ initialKwh = 20000 }: { initialKwh?: number }) {
  const { bih, eu } = useGridRows()
  const carFactor = useFactorMap().map['car_average']
  const [kwh, setKwh] = useState(initialKwh)
  const kgElec = bih ? (kwh * bih) / 1000 : 0
  const kgElecEu = eu ? (kwh * eu) / 1000 : 0
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="size-4" /> Electricity bill → CO₂
        </CardTitle>
        <CardDescription>From the club's yearly kWh (on the electricity bill)</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <NumberField id="kwh" label="kWh per year" value={kwh} onChange={setKwh} step={500} />
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-md border p-3">
            <p className="text-muted-foreground">In Bosnia and Herzegovina</p>
            <p className="text-2xl font-semibold tabular-nums">{formatNumber(kgElec)} kg</p>
            <p className="text-xs text-muted-foreground">{carKm(kgElec, carFactor)}</p>
          </div>
          <div className="rounded-md border p-3">
            <p className="text-muted-foreground">Same use on the EU grid</p>
            <p className="text-2xl font-semibold tabular-nums">{formatNumber(kgElecEu)} kg</p>
            <p className="text-xs text-muted-foreground">{carKm(kgElecEu, carFactor)}</p>
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          Every kWh saved in BiH avoids {bih ? formatNumber(bih) : '–'} g CO₂. Source: Ember.
        </p>
      </CardContent>
    </Card>
  )
}
