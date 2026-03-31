import { Badge } from '@/components/ui/badge'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import type { ValidationItem } from '@/lib/types'
import { AccuracyChart } from './AccuracyChart'
import { Trophy, Target } from 'lucide-react'

interface AccuracyComparisonProps {
  validation: ValidationItem[]
}

function statusBadge(status: ValidationItem['status']) {
  switch (status) {
    case 'exact':
      return <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/15">EXACT</Badge>
    case 'close':
      return <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/20 hover:bg-amber-500/15">CLOSE</Badge>
    case 'acceptable':
      return <Badge className="bg-sky-500/15 text-sky-400 border-sky-500/20 hover:bg-sky-500/15">OK</Badge>
    case 'miss':
      return <Badge className="bg-red-500/15 text-red-400 border-red-500/20 hover:bg-red-500/15">MISS</Badge>
  }
}

function statusRowColor(status: ValidationItem['status']): string {
  switch (status) {
    case 'exact': return ''
    case 'close': return 'bg-amber-500/5'
    case 'acceptable': return 'bg-sky-500/5'
    case 'miss': return 'bg-red-500/5'
  }
}

export function AccuracyComparison({ validation }: AccuracyComparisonProps) {
  const exact = validation.filter(v => v.status === 'exact').length
  const close = validation.filter(v => v.status === 'close').length
  const acceptable = validation.filter(v => v.status === 'acceptable').length
  const misses = validation.filter(v => v.status === 'miss').length
  const total = validation.length
  const accuracyPct = total > 0 ? Math.round((exact / total) * 100) : 0

  return (
    <div className="flex flex-col gap-5">
      {/* Hero stat */}
      <div className={`border rounded-sm p-5 text-center ${
        accuracyPct === 100 ? 'border-primary/30 bg-primary/5' : 'border-border bg-card'
      }`}>
        <div className="flex items-center justify-center gap-2 mb-3">
          {accuracyPct === 100 ? (
            <Trophy className="h-4 w-4 text-amber-400" />
          ) : (
            <Target className="h-4 w-4 text-primary" />
          )}
          <h2 className="text-xs font-semibold text-foreground uppercase tracking-wider">AI vs. Senior Estimator</h2>
        </div>
        <p className="text-3xl font-semibold font-mono tabular-nums text-primary">
          {exact}<span className="text-muted-foreground text-lg">/{total}</span> <span className="text-sm text-foreground font-sans">Exact Matches</span>
        </p>
        <p className="text-xs text-muted-foreground mt-2 font-mono">
          {accuracyPct}% accuracy — calibrated with historical bid data
        </p>

        {/* Mini breakdown */}
        <div className="flex justify-center gap-5 mt-4">
          <MiniStat label="Exact" count={exact} color="text-emerald-400" />
          <MiniStat label="Close" count={close} color="text-amber-400" />
          <MiniStat label="OK" count={acceptable} color="text-sky-400" />
          <MiniStat label="Miss" count={misses} color="text-red-400" />
        </div>
      </div>

      {/* Category chart */}
      <div className="border border-border rounded-sm bg-card p-5">
        <AccuracyChart details={validation} />
      </div>

      {/* Item-by-item comparison */}
      <div className="border border-border rounded-sm bg-card">
        <div className="px-4 py-3 border-b border-border">
          <h3 className="text-[10px] font-semibold text-muted-foreground uppercase tracking-widest">Item-by-Item Comparison</h3>
        </div>
        <Table>
          <TableHeader>
            <TableRow className="bg-secondary/50 hover:bg-secondary/50">
              <TableHead>Item</TableHead>
              <TableHead className="text-right">Estimator</TableHead>
              <TableHead className="text-right">AI</TableHead>
              <TableHead className="text-right">Diff</TableHead>
              <TableHead className="text-center">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {validation.map(v => (
              <TableRow key={v.item} className={statusRowColor(v.status)}>
                <TableCell className="text-xs py-1.5 text-foreground">{v.item}</TableCell>
                <TableCell className="text-right font-mono tabular-nums text-xs py-1.5 text-muted-foreground">{v.expected}</TableCell>
                <TableCell className="text-right font-mono tabular-nums text-xs py-1.5 text-foreground">{v.actual}</TableCell>
                <TableCell className="text-right font-mono tabular-nums text-xs py-1.5">
                  <span className={v.difference === 0 ? 'text-muted-foreground/40' : v.difference > 0 ? 'text-amber-400' : 'text-red-400'}>
                    {v.difference === 0 ? '0' : v.difference > 0 ? `+${v.difference}` : v.difference}
                  </span>
                </TableCell>
                <TableCell className="text-center py-1.5">{statusBadge(v.status)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

function MiniStat({ label, count, color }: { label: string; count: number; color: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className={`font-mono tabular-nums font-semibold text-sm ${color}`}>
        {count}
      </span>
      <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</span>
    </div>
  )
}
