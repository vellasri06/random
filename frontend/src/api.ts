import axios from 'axios'
import type { MomResponse } from './types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function generateMom({ transcript, file }: { transcript?: string; file?: File | null }): Promise<MomResponse> {
  const form = new FormData()
  if (transcript && transcript.trim().length > 0) form.append('transcript', transcript)
  if (file) form.append('file', file)

  const resp = await axios.post(`${API_BASE}/generate-mom`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return resp.data as MomResponse
}
