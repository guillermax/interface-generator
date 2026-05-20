import { useEffect, useState } from 'react'
import ChatHistory from './ChatHistory'
import ChatInput from './ChatInput'
import PreviewPanel from './PreviewPanel'
import type { FullResult, HistoryItem, Message } from '../types'
import { generateInterface, getHistory, getHistoryItem } from '../api'

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)
  const [dbHistory, setDbHistory] = useState<HistoryItem[]>([])

  const loadHistory = async () => {
    try {
      const items = await getHistory()
      setDbHistory(items)
    } catch {
      // history is non-critical; ignore errors silently
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  const handleSelectHistoryItem = async (item: HistoryItem) => {
    try {
      const full: FullResult = await getHistoryItem(item.request_id)
      const msg: Message = {
        id: item.request_id,
        text: `Interface generated in ${full.generation_time_ms ?? '?'}ms`,
        role: 'assistant',
        timestamp: new Date(item.created_at),
        preview: { html: full.html, css: full.css },
      }
      setSelectedMessage(msg)
    } catch {
      // ignore — item may not have a result yet
    }
  }

  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      role: 'user',
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])

    try {
      const result = await generateInterface(text)

      const assistantMessage: Message = {
        id: result.request_id,
        text: `Interface generated in ${result.generation_time_ms}ms`,
        role: 'assistant',
        timestamp: new Date(),
        preview: { html: result.html, css: result.css },
      }

      setMessages(prev => [...prev, assistantMessage])
      setSelectedMessage(assistantMessage)
      await loadHistory()
    } catch {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Unable to generate interface. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMessage])
      setSelectedMessage(assistantMessage)
    }
  }

  return (
    <div className="flex w-full h-full bg-gray-50">
      {/* Left sidebar - Chat history */}
      <ChatHistory
        messages={messages}
        selectedMessage={selectedMessage}
        onSelectMessage={setSelectedMessage}
        dbHistory={dbHistory}
        onSelectHistoryItem={handleSelectHistoryItem}
      />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <div className="text-center">
                <h1 className="text-4xl font-bold mb-4">Interface Generator</h1>
                <p>Describe an interface and get HTML/CSS code</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map(msg => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-md px-4 py-2 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-blue-500 text-white rounded-br-none'
                        : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <ChatInput onSendMessage={handleSendMessage} />
      </div>

      {/* Right sidebar - Preview panel */}
      {selectedMessage?.preview && (
        <PreviewPanel message={selectedMessage} />
      )}
    </div>
  )
}
