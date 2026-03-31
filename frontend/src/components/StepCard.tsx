import { CheckCircle, Circle, Loader2, AlertCircle } from 'lucide-react'
import type { PipelineStep } from '@/lib/types'

interface StepCardProps {
  step: PipelineStep
}

export function StepCard({ step }: StepCardProps) {
  return (
    <div className={`flex items-center gap-3 px-4 py-2.5 transition-opacity ${
      step.status === 'pending' ? 'opacity-50' : 'opacity-100'
    }`}>
      <StepIcon status={step.status} />
      <div className="flex-1 min-w-0">
        <span className={`text-xs font-medium ${
          step.status === 'active' ? 'text-primary' :
          step.status === 'complete' ? 'text-foreground' :
          'text-muted-foreground'
        }`}>
          <span className="font-mono text-muted-foreground mr-1.5">{String(step.step).padStart(2, '0')}</span>
          {step.name}
        </span>
        {step.status === 'complete' && step.result && (
          <p className="text-[10px] text-primary/70 mt-0.5 font-mono">{formatResult(step.result)}</p>
        )}
      </div>
      {step.status === 'active' && (
        <span className="text-[10px] text-primary font-mono animate-pulse tracking-wider">PROCESSING</span>
      )}
    </div>
  )
}

function StepIcon({ status }: { status: PipelineStep['status'] }) {
  switch (status) {
    case 'complete':
      return <CheckCircle className="h-4 w-4 text-primary shrink-0" />
    case 'active':
      return <Loader2 className="h-4 w-4 text-primary animate-spin shrink-0" />
    case 'error':
      return <AlertCircle className="h-4 w-4 text-destructive shrink-0" />
    default:
      return <Circle className="h-4 w-4 text-muted-foreground/30 shrink-0" />
  }
}

function formatResult(result: Record<string, unknown>): string {
  const parts: string[] = []
  for (const [key, val] of Object.entries(result)) {
    if (typeof val === 'number') {
      const label = key.replace(/_/g, ' ')
      parts.push(`${val} ${label}`)
    }
  }
  return parts.length > 0 ? parts.join(' · ') : ''
}
