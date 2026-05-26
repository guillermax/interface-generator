import { useEffect, useRef, useState } from 'react'
import ChatHistory from './ChatHistory'
import ChatInput from './ChatInput'
import PreviewPanel from './PreviewPanel'
import type { ConversationItem, Message } from '../types'
import {
  deleteConversation,
  generateInterface,
  getConversationMessages,
  getConversations,
} from '../api'

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)
  const [conversations, setConversations] = useState<ConversationItem[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadConversations = async () => {
    try {
      const items = await getConversations()
      setConversations(items)
    } catch {
      // non-critical
    }
  }

  useEffect(() => {
    loadConversations()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isGenerating])

  const handleNewChat = () => {
    setMessages([])
    setSelectedMessage(null)
    setCurrentConversationId(null)
  }

  const handleSelectConversation = async (conversationId: string) => {
    setCurrentConversationId(conversationId)
    try {
      const msgs = await getConversationMessages(conversationId)
      const rebuilt: Message[] = []
      for (const m of msgs) {
        rebuilt.push({
          id: `user-${m.request_id}`,
          text: m.text,
          role: 'user',
          timestamp: new Date(m.created_at),
        })
        if (m.html && m.css) {
          rebuilt.push({
            id: m.request_id,
            text: `Интерфейс сгенерирован за ${m.generation_time_ms ?? '?'} мс`,
            role: 'assistant',
            timestamp: new Date(m.created_at),
            preview: { html: m.html, css: m.css },
          })
        }
      }
      setMessages(rebuilt)
      const lastWithPreview = [...rebuilt].reverse().find(m => m.preview)
      setSelectedMessage(lastWithPreview ?? null)
    } catch {
      // ignore
    }
  }

  const handleDeleteConversation = async (conversationId: string) => {
    try {
      await deleteConversation(conversationId)
      setConversations(prev => prev.filter(c => c.conversation_id !== conversationId))
      if (currentConversationId === conversationId) {
        handleNewChat()
      }
    } catch {
      // ignore
    }
  }

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
      const result = await generateInterface(text, currentConversationId ?? undefined)
      const assistantMessage: Message = {
        id: result.request_id,
        text: `Интерфейс сгенерирован за ${result.generation_time_ms} мс`,
        role: 'assistant',
        timestamp: new Date(),
        preview: { html: result.html, css: result.css },
      }
      setMessages(prev => [...prev, assistantMessage])
      setSelectedMessage(assistantMessage)
      setCurrentConversationId(result.conversation_id)
      await loadConversations()
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
    <div className="flex w-full h-full bg-gray-50 overflow-hidden">

      {/* Левая колонка — история чатов */}
      <div className="shrink-0 self-stretch">
        <ChatHistory
          conversations={conversations}
          activeConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
          onNewChat={handleNewChat}
          selectedMessage={selectedMessage}
        />
      </div>

      {/* Средняя колонка — чат */}
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

      {/* Правая колонка — превью */}
      {selectedMessage?.preview && (
        <div className="shrink-0 min-w-0">
          <PreviewPanel message={selectedMessage} />
        </div>
      )}
    </div>
  )
}
