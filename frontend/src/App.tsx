import { useState } from 'react'
import type { AppState, TakeoffResults, PipelineStep } from './lib/types'
import { uploadPdf } from './lib/api'
import { Header } from './components/Header'
import { UploadZone } from './components/UploadZone'

export default function App() {
  const [state, setState] = useState<AppState>('idle')
  const [_results, setResults] = useState<TakeoffResults | null>(null)
  const [_steps, setSteps] = useState<PipelineStep[]>([])
  const [_jobId, setJobId] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  // Placeholders until later phases
  void setResults
  void setSteps

  async function handleUpload(file: File) {
    setIsUploading(true)
    try {
      const { job_id } = await uploadPdf(file)
      setJobId(job_id)
      setState('processing')
    } catch (err) {
      console.error('Upload failed:', err)
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      <Header />
      <main className="max-w-6xl mx-auto px-6 py-10">
        {state === 'idle' && (
          <UploadZone onUpload={handleUpload} isUploading={isUploading} />
        )}
        {state === 'processing' && (
          <div className="text-center text-muted-foreground">
            <p className="text-lg">Processing view coming in Phase 4 (job: {_jobId})</p>
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
