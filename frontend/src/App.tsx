import { useState } from 'react'
import type { AppState, TakeoffResults, PipelineStep } from './lib/types'
import { Header } from './components/Header'

export default function App() {
  const [state, setState] = useState<AppState>('idle')
  const [_results, setResults] = useState<TakeoffResults | null>(null)
  const [_steps, setSteps] = useState<PipelineStep[]>([])

  // Prevent unused variable warnings during Phase 2 scaffolding
  void setResults
  void setSteps
  void setState

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      <Header />
      <main className="max-w-6xl mx-auto px-6 py-10">
        {state === 'idle' && (
          <div className="text-center text-muted-foreground">
            <p className="text-lg">Upload page coming in Phase 3</p>
          </div>
        )}
        {state === 'processing' && (
          <div className="text-center text-muted-foreground">
            <p className="text-lg">Processing view coming in Phase 4</p>
          </div>
        )}
        {state === 'results' && (
          <div className="text-center text-muted-foreground">
            <p className="text-lg">Results dashboard coming in Phase 5</p>
          </div>
        )}
      </main>
    </div>
  )
}
