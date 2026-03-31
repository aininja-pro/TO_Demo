import { BarChart3, Clock, Layers, GitBranch, Target, PieChart } from 'lucide-react'
import type { TakeoffResults } from '@/lib/types'

interface StatsBarProps {
  results: TakeoffResults
}

export function StatsBar({ results }: StatsBarProps) {
  const totalValidation = results.validation?.length ?? 0
  const totalItems = totalValidation || Object.keys(results.materials).length
  const derivedKeys = new Set(Object.keys(results.derived_materials))
  const demoKeys = new Set(Object.keys(results.demo_items))
  const countedItems = Object.keys(results.materials).filter(k => !derivedKeys.has(k) && !demoKeys.has(k)).length
  const derivedItems = Object.keys(results.derived_materials).length
  const demoItems = Object.keys(results.demo_items).filter(k => (results.demo_items[k] ?? 0) > 0).length

  const exactMatches = results.validation?.filter(v => v.status === 'exact').length ?? 0
  const accuracyPct = totalValidation > 0 ? Math.round((exactMatches / totalValidation) * 100) : null

  return (
    <div className="grid grid-cols-4 md:grid-cols-7 gap-px bg-border rounded-sm overflow-hidden border border-border">
      <Stat icon={<BarChart3 className="h-3.5 w-3.5" />} label="Items" value={totalItems} />
      <Stat icon={<Clock className="h-3.5 w-3.5" />} label="Time" value={`${results.elapsed}s`} />
      <Stat icon={<Layers className="h-3.5 w-3.5" />} label="Counted" value={countedItems} />
      <Stat icon={<PieChart className="h-3.5 w-3.5" />} label="Derived" value={derivedItems} />
      <Stat icon={<Layers className="h-3.5 w-3.5" />} label="Demo" value={demoItems} />
      <Stat icon={<GitBranch className="h-3.5 w-3.5" />} label="Routing" value={results.routing_method?.replace(/_/g, ' ') || '—'} small />
      {accuracyPct !== null && (
        <Stat
          icon={<Target className="h-3.5 w-3.5" />}
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
    <div className={`bg-card px-3 py-3 flex flex-col items-center gap-1 ${highlight ? 'bg-primary/5' : ''}`}>
      <div className={`${highlight ? 'text-primary' : 'text-muted-foreground'}`}>
        {icon}
      </div>
      <div className={`font-mono tabular-nums font-semibold ${small ? 'text-xs' : 'text-lg'} ${highlight ? 'text-primary' : 'text-foreground'}`}>
        {value}
      </div>
      <div className="text-[9px] text-muted-foreground uppercase tracking-widest font-medium">{label}</div>
    </div>
  )
}
