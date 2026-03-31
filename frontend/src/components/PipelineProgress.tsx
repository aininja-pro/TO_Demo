import type { PipelineStep } from '@/lib/types'
import { Progress } from '@/components/ui/progress'
import { StepCard } from './StepCard'
import { FileText, Clock } from 'lucide-react'

interface PipelineProgressProps {
  steps: PipelineStep[]
  currentStep: number
  elapsedTime: number
  filename?: string
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return mins > 0
    ? `${mins}:${secs.toFixed(1).padStart(4, '0')}`
    : `00:${secs.toFixed(1).padStart(4, '0')}`
}

export function PipelineProgress({ steps, currentStep, elapsedTime, filename }: PipelineProgressProps) {
  const completedSteps = steps.filter(s => s.status === 'complete').length
  const progressPct = Math.round((completedSteps / steps.length) * 100)

  return (
    <div className="max-w-xl mx-auto flex flex-col gap-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-lg font-semibold text-foreground mb-1">Analyzing Your Drawings</h2>
        {filename && (
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <FileText className="h-3.5 w-3.5" />
            <span className="font-mono">{filename}</span>
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div>
        <Progress value={progressPct} />
        <div className="flex justify-between mt-2">
          <span className="text-[10px] text-muted-foreground font-mono tabular-nums tracking-wider">
            STEP {currentStep || 1}/{steps.length}
          </span>
          <span className="text-[10px] text-muted-foreground font-mono tabular-nums">
            {progressPct}%
          </span>
        </div>
      </div>

      {/* Steps */}
      <div className="border border-border rounded-sm divide-y divide-border/50">
        {steps.map(step => (
          <StepCard key={step.step} step={step} />
        ))}
      </div>

      {/* Timer */}
      <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
        <Clock className="h-3.5 w-3.5" />
        <span className="font-mono tabular-nums">{formatTime(elapsedTime)}</span>
      </div>
    </div>
  )
}
