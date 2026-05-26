import type { ConversationItem, Message } from '../types'

interface ChatHistoryProps {
  conversations: ConversationItem[]
  activeConversationId: string | null
  onSelectConversation: (conversationId: string) => void
  onDeleteConversation: (conversationId: string) => void
  onNewChat: () => void
  selectedMessage: Message | null
}

export default function ChatHistory({
  conversations,
  activeConversationId,
  onSelectConversation,
  onDeleteConversation,
  onNewChat,
  selectedMessage: _selectedMessage,
}: ChatHistoryProps) {
  const handleDelete = (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation()
    if (confirm('Удалить этот чат?')) {
      onDeleteConversation(conversationId)
    }
  }

  return (
    <div className="w-64 h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          className="w-full bg-sky-600 hover:bg-sky-700 text-white font-semibold py-2 px-4 rounded-lg transition"
          onClick={onNewChat}
        >
          + New Chat
        </button>
      </div>

      {/* Conversations list */}
      <div className="flex-1 overflow-y-auto p-2 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-thumb]:rounded-full">
        {conversations.length === 0 ? (
          <p className="text-xs text-gray-400 text-center mt-6 px-3">
            Нет сохранённых чатов
          </p>
        ) : (
          <>
            <p className="text-xs text-gray-400 px-3 py-1 uppercase tracking-wide">Chats</p>
            {conversations.map(conv => (
              <div
                key={conv.conversation_id}
                className={`group relative flex items-center rounded-lg mb-1 transition cursor-pointer ${
                  activeConversationId === conv.conversation_id
                    ? 'bg-sky-100 text-sky-900'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                onClick={() => onSelectConversation(conv.conversation_id)}
              >
                <div className="flex-1 min-w-0 px-3 py-2 pr-8">
                  <p className="text-sm truncate">{conv.title}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {conv.message_count} {conv.message_count === 1 ? 'сообщение' : 'сообщений'}
                  </p>
                </div>
                <button
                  onClick={e => handleDelete(e, conv.conversation_id)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition p-1 rounded"
                  title="Удалить чат"
                >
                  ×
                </button>
              </div>
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
