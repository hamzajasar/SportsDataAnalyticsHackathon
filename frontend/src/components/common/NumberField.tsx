import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

/** Labelled number input used by calculators and the club form. */
export function NumberField({
  id,
  label,
  value,
  onChange,
  min = 0,
  step = 1,
  hint,
}: {
  id: string
  label: string
  value: number
  onChange: (v: number) => void
  min?: number
  step?: number
  hint?: string
}) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type="number"
        inputMode="decimal"
        min={min}
        step={step}
        value={Number.isFinite(value) ? value : ''}
        onChange={(e) => onChange(e.target.valueAsNumber)}
      />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}
