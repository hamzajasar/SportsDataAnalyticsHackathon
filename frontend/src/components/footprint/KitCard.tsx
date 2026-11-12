import { useState } from 'react'
import { Leaf, Shirt } from 'lucide-react'
import { NumberField } from '@/components/common/NumberField'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useFactorMap } from '@/hooks/use-footprint'
import { formatNumber } from '@/lib/format'
import { carKm } from '@/lib/footprint'

/** Producing new kit vs re-using it (UK GHG 2025 material factors). */
export function KitCard() {
  const { map: f } = useFactorMap()
  const [kits, setKits] = useState(40)
  const [kgPerKit, setKgPerKit] = useState(0.6)
  const kitNew = kits * kgPerKit * (f['material_clothing_new'] ?? 0)
  const kitReused = kits * kgPerKit * (f['material_clothing_reused'] ?? 0)
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shirt className="size-4" /> Kit: buy new or pass it on?
        </CardTitle>
        <CardDescription>
          Footprint of producing the kit a club hands out each season
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <NumberField id="kits" label="Kits per season" value={kits} onChange={setKits} />
          <NumberField
            id="kg"
            label="kg per kit"
            value={kgPerKit}
            onChange={setKgPerKit}
            step={0.1}
            hint="Assumption: shirt + shorts + socks"
          />
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-md border p-3">
            <p className="text-muted-foreground">All new</p>
            <p className="text-2xl font-semibold tabular-nums">{formatNumber(kitNew)} kg</p>
            <p className="text-xs text-muted-foreground">{carKm(kitNew, f['car_average'])}</p>
          </div>
          <div className="rounded-md border p-3">
            <p className="flex items-center gap-1 text-muted-foreground">
              <Leaf className="size-3" /> Re-used (kit swap)
            </p>
            <p className="text-2xl font-semibold tabular-nums">{formatNumber(kitReused)} kg</p>
            <p className="text-xs text-muted-foreground">{carKm(kitReused, f['car_average'])}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
