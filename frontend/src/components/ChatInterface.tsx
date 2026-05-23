import { useEffect, useRef, useState } from 'react'
import ChatHistory from './ChatHistory'
import ChatInput from './ChatInput'
import PreviewPanel from './PreviewPanel'
import type { FullResult, HistoryItem, Message } from '../types'
import { generateInterface, getHistory, getHistoryItem } from '../api'

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)
  const [dbHistory, setDbHistory] = useState<HistoryItem[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadHistory = async () => {
    try {
      const items = await getHistory()
      setDbHistory(items)
    } catch {
      // history is non-critical
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isGenerating])

  const handleSelectHistoryItem = async (item: HistoryItem) => {
    try {
      const full: FullResult = await getHistoryItem(item.request_id)
      const msg: Message = {
        id: item.request_id,
        text: `«${item.text}» — сгенерировано за ${full.generation_time_ms ?? '?'} мс`,
        role: 'assistant',
        timestamp: new Date(item.created_at),
        preview: { html: full.html, css: full.css },
      }
      setSelectedMessage(msg)
    } catch {
      // ignore
    }
  }

  // Returns Promise so ChatInput can await it for loading-state management
  const handleSendMessage = async (text: string): Promise<void> => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      role: 'user',
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])
    setIsGenerating(true)

    try {
      const result = await generateInterface(text)
      const assistantMessage: Message = {
        id: result.request_id,
        text: `Интерфейс сгенерирован за ${result.generation_time_ms} мс`,
        role: 'assistant',
        timestamp: new Date(),
        preview: { html: result.html, css: result.css },
      }
      setMessages(prev => [...prev, assistantMessage])
      setSelectedMessage(assistantMessage)
      await loadHistory()
    } catch (err) {
      const isNetworkError = err instanceof TypeError && err.message.includes('fetch')
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: isNetworkError
          ? 'Нет связи с сервером. Убедитесь, что бэкенд запущен.'
          : 'Ошибка при генерации. Попробуйте ещё раз.',
        role: 'assistant',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    // overflow-hidden предотвращает горизонтальный скролл на уровне layout
    <div className="flex w-full h-full bg-gray-50 overflow-hidden">

      {/* Левая колонка — история. shrink-0 держит фиксированную ширину */}
      <div className="shrink-0">
        <ChatHistory
          messages={messages}
          selectedMessage={selectedMessage}
          onSelectMessage={setSelectedMessage}
          dbHistory={dbHistory}
          onSelectHistoryItem={handleSelectHistoryItem}
        />
      </div>

      {/* Средняя колонка — чат. min-w-0 позволяет сжиматься ниже содержимого */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 && !isGenerating ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <div className="text-center">
                <div className="text-5xl mb-4">✦</div>
                <h2 className="text-2xl font-semibold text-gray-600 mb-2">Interface Generator</h2>
                <p className="text-sm">Опишите интерфейс — получите HTML и CSS</p>
                <div className="mt-6 grid grid-cols-2 gap-2 max-w-xs text-xs text-gray-500">
                  {[
                    'форма входа',
                    'слайдер с картинками',
                    'карточка товара',
                    'навигационное меню',
                  ].map(hint => (
                    <button
                      key={hint}
                      onClick={() => handleSendMessage(hint)}
                      className="px-3 py-2 rounded-lg border border-gray-200 hover:border-sky-400 hover:text-sky-600 transition text-left"
                    >
                      {hint}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4 max-w-2xl mx-auto">
              {messages.map(msg => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-sm px-4 py-2.5 rounded-2xl text-sm ${
                      msg.role === 'user'
                        ? 'bg-sky-600 text-white rounded-br-sm'
                        : 'bg-white text-gray-800 rounded-bl-sm border border-gray-200 shadow-sm'
                    }`}
                  >
                    {msg.text}
                    {msg.role === 'assistant' && msg.preview && (
                      <button
                        onClick={() => setSelectedMessage(msg)}
                        className="mt-1.5 block text-xs text-sky-500 hover:text-sky-700 underline underline-offset-2"
                      >
                        Открыть превью →
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {isGenerating && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                    <div className="flex gap-1.5 items-center">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <ChatInput onSendMessage={handleSendMessage} isLoading={isGenerating} />
      </div>

      {/* Правая колонка — превью. min-w-0 не даёт контенту распирать flex */}
      {selectedMessage?.preview && (
        <div className="shrink-0 min-w-0">
          <PreviewPanel message={selectedMessage} />
        </div>
      )}
    </div>
  )
}
