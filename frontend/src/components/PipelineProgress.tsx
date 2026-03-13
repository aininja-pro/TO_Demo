import type { PipelineStep } from '@/lib/types'
import { Progress } from '@/components/ui/progress'
import { Card, CardContent } from '@/components/ui/card'
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
    <div className="max-w-2xl mx-auto flex flex-col gap-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-1">Analyzing Your Drawings</h2>
        {filename && (
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <FileText className="h-4 w-4" />
            <span>{filename}</span>
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div>
        <Progress value={progressPct} className="h-3" />
        <div className="flex justify-between mt-2">
          <span className="text-xs text-muted-foreground font-mono tabular-nums">
            Step {currentStep || 1} of {steps.length}
          </span>
          <span className="text-xs text-muted-foreground font-mono tabular-nums">
            {progressPct}%
          </span>
        </div>
      </div>

      {/* Steps */}
      <Card>
        <CardContent className="pt-4 pb-3 divide-y divide-gray-100">
          {steps.map(step => (
            <StepCard key={step.step} step={step} />
          ))}
        </CardContent>
      </Card>

      {/* Timer */}
      <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
        <Clock className="h-4 w-4" />
        <span className="font-mono tabular-nums">{formatTime(elapsedTime)}</span>
      </div>
    </div>
  )
}
