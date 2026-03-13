import { useState } from 'react'
import { useTakeoff } from './hooks/useTakeoff'
import { Header } from './components/Header'
import { UploadZone } from './components/UploadZone'
import { PipelineProgress } from './components/PipelineProgress'

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

  // Placeholder until Phase 5
  void results
  void reset

  function handleUpload(file: File) {
    setFilename(file.name)
    uploadAndProcess(file)
  }

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      <Header />
      <main className="max-w-6xl mx-auto px-6 py-10">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center">
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
        {state === 'results' && (
          <div className="text-center text-muted-foreground">
            <p className="text-lg">Results dashboard coming in Phase 5</p>
          </div>
        )}
      </main>
    </div>
  )
}
