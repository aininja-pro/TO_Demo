import { useState, useRef, useCallback } from 'react'
import type { AppState, PipelineStep, TakeoffResults } from '@/lib/types'
import { uploadPdf } from '@/lib/api'

const PIPELINE_STEPS: Pick<PipelineStep, 'step' | 'name'>[] = [
  { step: 1, name: 'PDF Processing' },
  { step: 2, name: 'Reading Schedules' },
  { step: 3, name: 'Counting Symbols' },
  { step: 4, name: 'Routing Analysis' },
  { step: 5, name: 'Applying Business Rules' },
  { step: 6, name: 'Generating Output' },
]

export function useTakeoff() {
  const [state, setState] = useState<AppState>('idle')
  const [steps, setSteps] = useState<PipelineStep[]>(
    PIPELINE_STEPS.map(s => ({ ...s, status: 'pending' }))
  )
  const [currentStep, setCurrentStep] = useState(0)
  const [results, setResults] = useState<TakeoffResults | null>(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const startTimer = useCallback(() => {
    const start = Date.now()
    timerRef.current = setInterval(() => {
      setElapsedTime((Date.now() - start) / 1000)
    }, 100)
  }, [])

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [])

  const updateStep = useCallback((stepNum: number, status: PipelineStep['status'], result?: Record<string, unknown>) => {
    setSteps(prev => prev.map(s =>
      s.step === stepNum ? { ...s, status, ...(result ? { result } : {}) } : s
    ))
  }, [])

  const connectSSE = useCallback((jobId: string) => {
    const evtSource = new EventSource(`/api/takeoff/${jobId}/stream`)

    evtSource.addEventListener('step_start', (e) => {
      const data = JSON.parse(e.data)
      setCurrentStep(data.step)
      updateStep(data.step, 'active')
    })

    evtSource.addEventListener('step_complete', (e) => {
      const data = JSON.parse(e.data)
      updateStep(data.step, 'complete', data.result)
    })

    evtSource.addEventListener('complete', (e) => {
      const data = JSON.parse(e.data)
      stopTimer()
      setResults(data)
      setState('results')
      evtSource.close()
    })

    evtSource.addEventListener('error', (e) => {
      if (e instanceof MessageEvent) {
        const data = JSON.parse(e.data)
        setError(data.message)
        updateStep(data.step, 'error')
      }
      stopTimer()
      evtSource.close()
    })

    evtSource.onerror = () => {
      stopTimer()
      setError('Connection lost')
      evtSource.close()
    }
  }, [updateStep, stopTimer])

  const uploadAndProcess = useCallback(async (file: File) => {
    setIsUploading(true)
    setError(null)
    try {
      const { job_id } = await uploadPdf(file)
      setIsUploading(false)
      setState('processing')
      setSteps(PIPELINE_STEPS.map(s => ({ ...s, status: 'pending' })))
      setCurrentStep(0)
      setElapsedTime(0)
      startTimer()
      connectSSE(job_id)
    } catch (err) {
      setIsUploading(false)
      setError(err instanceof Error ? err.message : 'Upload failed')
    }
  }, [startTimer, connectSSE])

  const reset = useCallback(() => {
    stopTimer()
    setState('idle')
    setSteps(PIPELINE_STEPS.map(s => ({ ...s, status: 'pending' })))
    setCurrentStep(0)
    setResults(null)
    setElapsedTime(0)
    setError(null)
    setIsUploading(false)
  }, [stopTimer])

  return {
    state,
    steps,
    currentStep,
    results,
    elapsedTime,
    isUploading,
    error,
    uploadAndProcess,
    reset,
  }
}
