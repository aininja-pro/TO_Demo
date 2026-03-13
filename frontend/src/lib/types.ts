export type AppState = 'idle' | 'processing' | 'results'
export type StepStatus = 'pending' | 'active' | 'complete' | 'error'

export interface PipelineStep {
  step: number
  name: string
  status: StepStatus
  result?: Record<string, unknown>
}

export interface ValidationItem {
  item: string
  expected: number
  actual: number
  difference: number
  status: 'exact' | 'close' | 'acceptable' | 'miss'
}

export interface TakeoffResults {
  materials: Record<string, number>
  derived_materials: Record<string, number>
  demo_items: Record<string, number>
  conduit: Record<string, number>
  wire: Record<string, number>
  routing_method: string
  validation: ValidationItem[]
  formulas?: Record<string, string>
  sheets: { number: string; title: string; type: string }[]
  is_ivcc_project: boolean
  elapsed: number
}

export type MaterialCategory =
  | 'all' | 'fixtures' | 'controls' | 'power'
  | 'technology' | 'demo' | 'derived' | 'accuracy'
