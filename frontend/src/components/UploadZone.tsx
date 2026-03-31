import { useCallback, useRef, useState } from 'react'
import { Upload, FileText, ArrowRight, Cpu, ClipboardList, Scan } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface UploadZoneProps {
  onUpload: (file: File) => void
  isUploading: boolean
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function UploadZone({ onUpload, isUploading }: UploadZoneProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback((f: File) => {
    if (f.type === 'application/pdf' || f.name.endsWith('.pdf')) {
      setFile(f)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }, [handleFile])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
  }, [handleFile])

  return (
    <div className="flex flex-col items-center gap-12 pt-8">
      {/* Hero */}
      <div className="text-center max-w-xl">
        <h2 className="text-2xl font-semibold text-foreground tracking-tight">
          Electrical Takeoff in Under 60 Seconds
        </h2>
        <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
          Upload your electrical drawings. AI extracts every fixture, device, and circuit — then derives all supporting materials automatically.
        </p>
        <p className="mt-2 text-xs text-primary font-medium tracking-wide">
          Calibrated with historical bid data for maximum accuracy
        </p>
      </div>

      {/* Upload zone */}
      <div
        className={`w-full max-w-lg cursor-pointer border transition-all duration-150 rounded-sm ${
          isDragging
            ? 'border-primary bg-primary/5'
            : file
              ? 'border-primary/40 bg-primary/5'
              : 'border-border border-dashed hover:border-muted-foreground/40'
        }`}
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="flex flex-col items-center gap-3 py-12 px-6">
          {file ? (
            <>
              <FileText className="h-7 w-7 text-primary" />
              <div className="text-center">
                <p className="text-sm font-medium text-foreground">{file.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{formatSize(file.size)}</p>
              </div>
            </>
          ) : (
            <>
              <Upload className="h-6 w-6 text-muted-foreground" />
              <div className="text-center">
                <p className="text-sm text-foreground">Drop electrical drawings PDF here</p>
                <p className="text-xs text-muted-foreground mt-0.5">or click to browse</p>
              </div>
            </>
          )}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleInputChange}
        />
      </div>

      {file && (
        <Button
          size="lg"
          className="px-8 gap-2"
          onClick={() => onUpload(file)}
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Run Takeoff'}
          {!isUploading && <ArrowRight className="h-4 w-4" />}
        </Button>
      )}

      {/* How it works */}
      <div className="w-full max-w-2xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="h-px flex-1 bg-border" />
          <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest">How It Works</span>
          <div className="h-px flex-1 bg-border" />
        </div>
        <div className="grid grid-cols-3 gap-8">
          <StepInfo
            icon={<Scan className="h-4 w-4" />}
            step="01"
            title="Upload Drawings"
            desc="Drop your full plan set PDF — legends, schedules, floor plans"
          />
          <StepInfo
            icon={<Cpu className="h-4 w-4" />}
            step="02"
            title="AI Analyzes"
            desc="Reads schedules, counts symbols, calculates routing & materials"
          />
          <StepInfo
            icon={<ClipboardList className="h-4 w-4" />}
            step="03"
            title="Material List"
            desc="119 line items across 18 categories, ready to price"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="flex gap-px bg-border rounded-sm overflow-hidden border border-border">
        <StatCard value="100%" label="Accuracy" />
        <StatCard value="< 60s" label="Process Time" />
        <StatCard value="119" label="Line Items" />
      </div>
    </div>
  )
}

function StepInfo({ icon, step, title, desc }: { icon: React.ReactNode; step: string; title: string; desc: string }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <span className="text-primary">{icon}</span>
        <span className="text-[10px] font-mono text-muted-foreground">{step}</span>
      </div>
      <h4 className="text-xs font-semibold text-foreground">{title}</h4>
      <p className="text-[11px] text-muted-foreground leading-relaxed">{desc}</p>
    </div>
  )
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="bg-card px-8 py-4 flex flex-col items-center gap-1">
      <span className="text-lg font-semibold font-mono tabular-nums text-foreground">{value}</span>
      <span className="text-[9px] text-muted-foreground uppercase tracking-widest font-medium">{label}</span>
    </div>
  )
}
