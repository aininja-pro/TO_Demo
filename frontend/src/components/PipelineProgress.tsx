import type { PipelineStep } from '@/lib/types'
import { Progress } from '@/components/ui/progress'
import { Card, CardContent } from '@/components/ui/card'
import { StepCard } from './StepCard'

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
      {filename && (
        <p className="text-base text-center">
          Processing: <span className="font-medium">{filename}</span>
        </p>
      )}

      <Progress value={progressPct} className="h-3" />
      <p className="text-sm text-center text-muted-foreground font-mono tabular-nums">
        {progressPct}% — Step {currentStep || 1} of {steps.length}
      </p>

      <Card>
        <CardContent className="pt-5 pb-4">
          {steps.map(step => (
            <StepCard key={step.step} step={step} />
          ))}
        </CardContent>
      </Card>

      <p className="text-center text-sm text-muted-foreground font-mono tabular-nums">
        Elapsed: {formatTime(elapsedTime)}
      </p>
    </div>
  )
}
