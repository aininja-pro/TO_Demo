import { useState } from 'react'
import { useTakeoff } from './hooks/useTakeoff'
import { Header } from './components/Header'
import { UploadZone } from './components/UploadZone'
import { PipelineProgress } from './components/PipelineProgress'
import { ResultsDashboard } from './components/ResultsDashboard'
import { Button } from './components/ui/button'
import { ArrowLeft } from 'lucide-react'

export default function App() {
  const {
    state,
    steps,
    currentStep,
    results,
    elapsedTime,
    isUploading,
    error,
    uploadAndProcess,
    reset,
  } = useTakeoff()

  const [filename, setFilename] = useState<string | null>(null)

  function handleUpload(file: File) {
    setFilename(file.name)
    uploadAndProcess(file)
  }

  return (
    <div className="min-h-screen bg-background">
      <Header>
        {state === 'results' && (
          <Button
            variant="outline"
            size="sm"
            onClick={reset}
            className="gap-1.5"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            New Takeoff
          </Button>
        )}
      </Header>
      <main className={`mx-auto px-6 py-8 ${state === 'results' ? 'max-w-7xl' : 'max-w-5xl'}`}>
        {error && (
          <div className="mb-6 p-3 bg-destructive/10 border border-destructive/30 rounded-sm text-destructive text-sm text-center">
            {error}
          </div>
        )}
        {state === 'idle' && (
          <UploadZone onUpload={handleUpload} isUploading={isUploading} />
        )}
        {state === 'processing' && (
          <PipelineProgress
            steps={steps}
            currentStep={currentStep}
            elapsedTime={elapsedTime}
            filename={filename ?? undefined}
          />
        )}
        {state === 'results' && results && (
          <ResultsDashboard results={results} />
        )}
      </main>
    </div>
  )
}
