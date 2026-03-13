export async function uploadPdf(file: File): Promise<{ job_id: string; filename: string }> {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch('/api/takeoff', {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.status} ${res.statusText}`)
  }

  return res.json()
}
