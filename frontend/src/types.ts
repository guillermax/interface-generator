export interface Message {
  id: string
  text: string
  role: 'user' | 'assistant'
  timestamp: Date
  preview?: {
    html: string
    css: string
  }
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
}

export interface HistoryItem {
  request_id: string
  text: string
  created_at: string
  status: string
}

export interface FullResult extends HistoryItem {
  html: string
  css: string
  ami_graph: Record<string, unknown> | null
  generation_time_ms: number | null
}
