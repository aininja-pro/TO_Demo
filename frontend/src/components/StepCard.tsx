import { CheckCircle, Circle, Loader2, AlertCircle } from 'lucide-react'
import type { PipelineStep } from '@/lib/types'

interface StepCardProps {
  step: PipelineStep
}

export function StepCard({ step }: StepCardProps) {
  return (
    <div className="flex items-center gap-3 py-2">
      <StepIcon status={step.status} />
      <div className="flex-1">
        <span className={step.status === 'active' ? 'font-medium' : ''}>
          Step {step.step}: {step.name}
          {step.status === 'active' && '...'}
        </span>
      </div>
      {step.status === 'complete' && step.result && (
        <span className="text-sm text-muted-foreground font-mono tabular-nums">
          {formatResult(step.result)}
        </span>
      )}
    </div>
  )
}

function StepIcon({ status }: { status: PipelineStep['status'] }) {
  switch (status) {
    case 'complete':
      return <CheckCircle className="h-5 w-5 text-green-600 shrink-0" />
    case 'active':
      return <Loader2 className="h-5 w-5 text-[#2563eb] animate-spin shrink-0" />
    case 'error':
      return <AlertCircle className="h-5 w-5 text-red-600 shrink-0" />
    default:
      return <Circle className="h-5 w-5 text-gray-300 shrink-0" />
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
  return parts.join(', ')
}
