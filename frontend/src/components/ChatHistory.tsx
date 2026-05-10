import { Message } from '../types'

interface ChatHistoryProps {
  messages: Message[]
  selectedMessage: Message | null
  onSelectMessage: (message: Message) => void
}

export default function ChatHistory({
  messages,
  selectedMessage,
  onSelectMessage,
}: ChatHistoryProps) {
  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition">
          + New Chat
        </button>
      </div>
      
      {/* History */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2">
          {messages
            .filter(msg => msg.role === 'user')
            .map(msg => (
              <button
                key={msg.id}
                onClick={() => onSelectMessage(msg)}
                className={`w-full text-left px-3 py-2 rounded-lg mb-2 truncate text-sm transition ${
                  selectedMessage?.id === msg.id
                    ? 'bg-blue-100 text-blue-900'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {msg.text.substring(0, 50)}...
              </button>
            ))}
        </div>
      </div>
      
      {/* Footer */}
      <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
        <p>© 2024 Interface Generator</p>
      </div>
    </div>
  )
}
