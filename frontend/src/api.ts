import type { FullResult, HistoryItem } from './types'

export interface GenerateResponse {
  request_id: string
  html: string
  css: string
  generation_time_ms: number
}

// Dev: VITE_API_BASE_URL=http://localhost:8000 (из .env.development)
// Prod: VITE_API_BASE_URL=''              (из .env.production → относительные пути)
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const BASE = `${API_BASE}/api`

export async function generateInterface(text: string): Promise<GenerateResponse> {
  const response = await fetch(`${BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`)
  }
  return response.json()
}

export async function getHistory(): Promise<HistoryItem[]> {
  const response = await fetch(`${BASE}/history`)
  if (!response.ok) {
    throw new Error(`History request failed with status ${response.status}`)
  }
  return response.json()
}

export async function getHistoryItem(requestId: string): Promise<FullResult> {
  const response = await fetch(`${BASE}/history/${requestId}`)
  if (!response.ok) {
    throw new Error(`History item request failed with status ${response.status}`)
  }
  return response.json()
}
