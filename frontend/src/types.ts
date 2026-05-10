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
