import { useCallback, useRef, useState } from 'react'
import { Upload, FileText } from 'lucide-react'
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
    <div className="flex flex-col items-center gap-8">
      <Card
        className={`w-full max-w-xl cursor-pointer border-2 border-dashed transition-colors ${
          isDragging ? 'border-[#2563eb] bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <CardContent className="flex flex-col items-center gap-3 py-12">
          {file ? (
            <>
              <FileText className="h-10 w-10 text-[#2563eb]" />
              <p className="text-base font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground">{formatSize(file.size)}</p>
            </>
          ) : (
            <>
              <Upload className="h-10 w-10 text-muted-foreground" />
              <p className="text-base font-medium">Drop electrical drawings PDF here</p>
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
          className="bg-[#2563eb] hover:bg-[#1d4ed8] text-white px-8"
          onClick={() => onUpload(file)}
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload & Process'}
        </Button>
      )}

      {/* Landing stat cards */}
      <div className="flex gap-6 mt-4">
        <StatCard icon="⚡" value="< 60s" label="Process Time" />
        <StatCard icon="🎯" value="97%" label="Accuracy Proven" />
        <StatCard icon="📊" value="119" label="Line Items" />
      </div>
    </div>
  )
}

function StatCard({ icon, value, label }: { icon: string; value: string; label: string }) {
  return (
    <Card className="w-36 text-center">
      <CardContent className="pt-5 pb-4 flex flex-col items-center gap-1">
        <span className="text-2xl">{icon}</span>
        <span className="text-lg font-semibold font-mono tabular-nums">{value}</span>
        <span className="text-xs text-muted-foreground">{label}</span>
      </CardContent>
    </Card>
  )
}
