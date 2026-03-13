import { useCallback, useRef, useState } from 'react'
import { Upload, FileText, FileSearch, Cpu, ClipboardList, Target, Timer, BarChart3 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
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
    <div className="flex flex-col items-center gap-10">
      {/* Hero section */}
      <div className="text-center max-w-2xl">
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight">
          Electrical Takeoff in Under 60 Seconds
        </h2>
        <p className="mt-3 text-lg text-gray-600">
          Upload your electrical drawings. Our AI extracts every fixture, device, and circuit —
          then derives all supporting materials automatically.
        </p>
        <p className="mt-2 text-sm text-[#2563eb] font-medium">
          Calibrated with your historical bid data for maximum accuracy
        </p>
      </div>

      {/* Upload zone */}
      <Card
        className={`w-full max-w-xl cursor-pointer border-2 border-dashed transition-all duration-200 ${
          isDragging
            ? 'border-[#2563eb] bg-blue-50 scale-[1.02] shadow-lg'
            : file
              ? 'border-[#2563eb]/40 bg-blue-50/50'
              : 'border-gray-300 hover:border-gray-400 hover:shadow-md'
        }`}
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <CardContent className="flex flex-col items-center gap-3 py-14">
          {file ? (
            <>
              <div className="bg-blue-100 rounded-full p-3">
                <FileText className="h-8 w-8 text-[#2563eb]" />
              </div>
              <p className="text-base font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-muted-foreground">{formatSize(file.size)}</p>
            </>
          ) : (
            <>
              <div className="bg-gray-100 rounded-full p-3">
                <Upload className="h-8 w-8 text-gray-400" />
              </div>
              <p className="text-base font-medium text-gray-700">Drop electrical drawings PDF here</p>
              <p className="text-sm text-muted-foreground">or click to browse</p>
            </>
          )}
        </CardContent>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleInputChange}
        />
      </Card>

      {file && (
        <Button
          size="lg"
          className="bg-[#2563eb] hover:bg-[#1d4ed8] text-white px-10 py-6 text-base shadow-lg hover:shadow-xl transition-all"
          onClick={() => onUpload(file)}
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Run Takeoff'}
        </Button>
      )}

      {/* How it works */}
      <div className="w-full max-w-3xl">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider text-center mb-5">How It Works</h3>
        <div className="grid grid-cols-3 gap-6">
          <StepInfo
            icon={<FileSearch className="h-6 w-6 text-[#2563eb]" />}
            step="1"
            title="Upload Drawings"
            desc="Drop your full plan set PDF — legends, schedules, floor plans"
          />
          <StepInfo
            icon={<Cpu className="h-6 w-6 text-[#2563eb]" />}
            step="2"
            title="AI Analyzes"
            desc="Reads schedules, counts symbols, calculates routing & materials"
          />
          <StepInfo
            icon={<ClipboardList className="h-6 w-6 text-[#2563eb]" />}
            step="3"
            title="Material List"
            desc="101 line items across 16 categories, ready to price"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="flex gap-5">
        <StatCard icon={<Target className="h-5 w-5 text-green-600" />} value="100%" label="Accuracy" />
        <StatCard icon={<Timer className="h-5 w-5 text-[#2563eb]" />} value="< 60s" label="Process Time" />
        <StatCard icon={<BarChart3 className="h-5 w-5 text-amber-600" />} value="101" label="Line Items" />
      </div>
    </div>
  )
}

function StepInfo({ icon, step, title, desc }: { icon: React.ReactNode; step: string; title: string; desc: string }) {
  return (
    <div className="flex flex-col items-center text-center gap-2.5">
      <div className="relative">
        <div className="bg-blue-50 rounded-xl p-3">{icon}</div>
        <span className="absolute -top-1.5 -right-1.5 bg-[#2563eb] text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">{step}</span>
      </div>
      <h4 className="font-semibold text-gray-900 text-sm">{title}</h4>
      <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
    </div>
  )
}

function StatCard({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) {
  return (
    <Card className="w-40 hover:shadow-md transition-shadow">
      <CardContent className="pt-5 pb-4 flex flex-col items-center gap-1.5">
        {icon}
        <span className="text-xl font-bold font-mono tabular-nums text-gray-900">{value}</span>
        <span className="text-xs text-muted-foreground">{label}</span>
      </CardContent>
    </Card>
  )
}
