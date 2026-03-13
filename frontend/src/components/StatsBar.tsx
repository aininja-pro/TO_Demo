import { Card, CardContent } from '@/components/ui/card'
import type { TakeoffResults } from '@/lib/types'

interface StatsBarProps {
  results: TakeoffResults
}

export function StatsBar({ results }: StatsBarProps) {
  const totalItems = Object.keys(results.materials).length
    + Object.keys(results.derived_materials).length
    + Object.keys(results.demo_items).length
  const countedItems = Object.keys(results.materials).length
  const derivedItems = Object.keys(results.derived_materials).length

  return (
    <div className="flex gap-4">
      <Stat label="Total Items" value={totalItems} />
      <Stat label="Time" value={`${results.elapsed}s`} />
      <Stat label="Counted" value={countedItems} />
      <Stat label="Derived" value={derivedItems} />
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <Card className="flex-1">
      <CardContent className="pt-4 pb-3 text-center">
        <div className="text-2xl font-semibold font-mono tabular-nums">{value}</div>
        <div className="text-xs text-muted-foreground mt-1">{label}</div>
      </CardContent>
    </Card>
  )
}
