import { useState } from 'react'
import ChatHistory from './ChatHistory'
import ChatInput from './ChatInput'
import PreviewPanel from './PreviewPanel'
import { Message } from '../types'

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)

  const handleSendMessage = async (text: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      role: 'user',
      timestamp: new Date(),
    }
    
    setMessages([...messages, userMessage])
    
    // Simulate API call with mock response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Generated a login form for you',
        role: 'assistant',
        timestamp: new Date(),
        preview: {
          html: `<form class="max-w-sm mx-auto p-6 bg-white rounded-lg shadow">
  <h2 class="text-2xl font-bold mb-6 text-gray-800">Login</h2>
  <div class="mb-4">
    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
    <input type="email" placeholder="Enter your email" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
  </div>
  <div class="mb-6">
    <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
    <input type="password" placeholder="Enter your password" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
  </div>
  <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition">Sign In</button>
</form>`,
          css: `body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}`
        }
      }
      
      setMessages(prev => [...prev, assistantMessage])
      setSelectedMessage(assistantMessage)
    }, 1000)
  }

  return (
    <div className="flex w-full h-full bg-gray-50">
      {/* Left sidebar - Chat history */}
      <ChatHistory 
        messages={messages}
        selectedMessage={selectedMessage}
        onSelectMessage={setSelectedMessage}
      />
      
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Messages display area */}
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
        
        {/* Chat input */}
        <ChatInput onSendMessage={handleSendMessage} />
      </div>
      
      {/* Right sidebar - Preview panel */}
      {selectedMessage && selectedMessage.preview && (
        <PreviewPanel message={selectedMessage} />
      )}
    </div>
  )
}
