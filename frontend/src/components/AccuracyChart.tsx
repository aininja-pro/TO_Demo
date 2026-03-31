import type { ValidationItem } from '@/lib/types'
import { getItemCategory } from '@/lib/items'

interface AccuracyChartProps {
  details: ValidationItem[]
}

function getBarColor(value: number): string {
  if (value >= 95) return 'bg-primary/40'
  if (value >= 80) return 'bg-amber-500/40'
  return 'bg-red-500/40'
}

export function AccuracyChart({ details }: AccuracyChartProps) {
  const byCategory = new Map<string, { matched: number; total: number }>()

  for (const item of details) {
    const cat = getItemCategory(item.item) ?? 'Other'
    const entry = byCategory.get(cat) ?? { matched: 0, total: 0 }
    entry.total++
    if (item.status === 'exact' || item.status === 'close' || item.status === 'acceptable') {
      entry.matched++
    }
    byCategory.set(cat, entry)
  }

  const data = Array.from(byCategory.entries())
    .map(([category, { matched, total }]) => ({
      category,
      accuracy: Math.round((matched / total) * 100),
      matched,
      total,
    }))
    .sort((a, b) => b.accuracy - a.accuracy)

  return (
    <div className="flex flex-col gap-2.5">
      <h3 className="text-[10px] font-semibold text-muted-foreground uppercase tracking-widest mb-1">Accuracy by Category</h3>
      {data.map(({ category, accuracy, matched, total }) => (
        <div key={category} className="flex items-center gap-3">
          <span className="text-[11px] text-muted-foreground w-24 text-right shrink-0">{category}</span>
          <div className="flex-1 bg-secondary rounded-sm h-4 overflow-hidden">
            <div
              className={`h-full rounded-sm transition-all duration-500 ${getBarColor(accuracy)}`}
              style={{ width: `${accuracy}%` }}
            />
          </div>
          <span className="text-[11px] font-mono tabular-nums text-muted-foreground w-20 shrink-0">
            {accuracy}% ({matched}/{total})
          </span>
        </div>
      ))}
    </div>
  )
}
