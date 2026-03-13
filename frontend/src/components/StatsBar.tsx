import { Card, CardContent } from '@/components/ui/card'
import { BarChart3, Clock, Layers, GitBranch, Target, PieChart } from 'lucide-react'
import type { TakeoffResults } from '@/lib/types'

interface StatsBarProps {
  results: TakeoffResults
}

export function StatsBar({ results }: StatsBarProps) {
  // Total = unique items validated against ground truth
  const totalValidation = results.validation?.length ?? 0
  const totalItems = totalValidation || Object.keys(results.materials).length
  // Counted = materials minus derived minus demo (the items extracted from plans/schedules)
  const derivedKeys = new Set(Object.keys(results.derived_materials))
  const demoKeys = new Set(Object.keys(results.demo_items))
  const countedItems = Object.keys(results.materials).filter(k => !derivedKeys.has(k) && !demoKeys.has(k)).length
  const derivedItems = Object.keys(results.derived_materials).length
  const demoItems = Object.keys(results.demo_items).filter(k => (results.demo_items[k] ?? 0) > 0).length

  const exactMatches = results.validation?.filter(v => v.status === 'exact').length ?? 0
  const accuracyPct = totalValidation > 0 ? Math.round((exactMatches / totalValidation) * 100) : null

  return (
    <div className="grid grid-cols-4 md:grid-cols-7 gap-3">
      <Stat
        icon={<BarChart3 className="h-4 w-4 text-[#2563eb]" />}
        label="Total Items"
        value={totalItems}
      />
      <Stat
        icon={<Clock className="h-4 w-4 text-amber-600" />}
        label="Process Time"
        value={`${results.elapsed}s`}
      />
      <Stat
        icon={<Layers className="h-4 w-4 text-purple-600" />}
        label="Counted"
        value={countedItems}
      />
      <Stat
        icon={<PieChart className="h-4 w-4 text-teal-600" />}
        label="Derived"
        value={derivedItems}
      />
      <Stat
        icon={<Layers className="h-4 w-4 text-red-500" />}
        label="Demo"
        value={demoItems}
      />
      <Stat
        icon={<GitBranch className="h-4 w-4 text-gray-600" />}
        label="Routing"
        value={results.routing_method?.replace(/_/g, ' ') || '—'}
        small
      />
      {accuracyPct !== null && (
        <Stat
          icon={<Target className="h-4 w-4 text-green-600" />}
          label="Accuracy"
          value={`${accuracyPct}%`}
          highlight={accuracyPct === 100}
        />
      )}
    </div>
  )
}

function Stat({ icon, label, value, small, highlight }: {
  icon: React.ReactNode
  label: string
  value: string | number
  small?: boolean
  highlight?: boolean
}) {
  return (
    <Card className={highlight ? 'ring-2 ring-green-200 bg-green-50/50' : ''}>
      <CardContent className="pt-3 pb-2.5 flex flex-col items-center gap-1">
        {icon}
        <div className={`font-semibold font-mono tabular-nums ${small ? 'text-sm' : 'text-xl'} ${highlight ? 'text-green-700' : ''}`}>
          {value}
        </div>
        <div className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</div>
      </CardContent>
    </Card>
  )
}
