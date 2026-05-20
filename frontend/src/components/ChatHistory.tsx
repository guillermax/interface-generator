import type { HistoryItem, Message } from '../types'

interface ChatHistoryProps {
  messages: Message[]
  selectedMessage: Message | null
  onSelectMessage: (message: Message) => void
  dbHistory: HistoryItem[]
  onSelectHistoryItem: (item: HistoryItem) => void
}

export default function ChatHistory({
  messages,
  selectedMessage,
  onSelectMessage,
  dbHistory,
  onSelectHistoryItem,
}: ChatHistoryProps) {
  const sessionItems = messages.filter(msg => msg.role === 'user')

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          className="w-full bg-sky-600 hover:bg-sky-700 text-white font-semibold py-2 px-4 rounded-lg transition"
          onClick={() => window.location.reload()}
        >
          + New Chat
        </button>
      </div>

      {/* This session */}
      {sessionItems.length > 0 && (
        <div className="p-2">
          <p className="text-xs text-gray-400 px-3 py-1 uppercase tracking-wide">This session</p>
          {sessionItems.map(msg => (
            <button
              key={msg.id}
              onClick={() => onSelectMessage(msg)}
              className={`w-full text-left px-3 py-2 rounded-lg mb-1 truncate text-sm transition ${
                selectedMessage?.id === msg.id
                  ? 'bg-sky-100 text-sky-900'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              {msg.text.length > 50 ? msg.text.substring(0, 50) + '…' : msg.text}
            </button>
          ))}
        </div>
      )}

      {/* DB history */}
      <div className="flex-1 overflow-y-auto p-2">
        {dbHistory.length > 0 && (
          <>
            <p className="text-xs text-gray-400 px-3 py-1 uppercase tracking-wide">History</p>
            {dbHistory.map(item => (
              <button
                key={item.request_id}
                onClick={() => onSelectHistoryItem(item)}
                className={`w-full text-left px-3 py-2 rounded-lg mb-1 truncate text-sm transition ${
                  selectedMessage?.id === item.request_id
                    ? 'bg-sky-100 text-sky-900'
                    : item.status === 'done'
                    ? 'text-gray-700 hover:bg-gray-100'
                    : 'text-gray-400 cursor-default'
                }`}
                disabled={item.status !== 'done'}
                title={item.text}
              >
                {item.text.length > 50 ? item.text.substring(0, 50) + '…' : item.text}
              </button>
            ))}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
        <p>© 2024 Interface Generator</p>
      </div>
    </div>
  )
}
