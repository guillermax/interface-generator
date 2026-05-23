import { useState } from 'react'
import type { Message } from '../types'

interface PreviewPanelProps {
  message: Message
}

export default function PreviewPanel({ message }: PreviewPanelProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview')
  const [copiedHtml, setCopiedHtml] = useState(false)
  const [copiedCss, setCopiedCss] = useState(false)

  if (!message.preview) return null

  const { html, css } = message.preview

  // Бэкенд возвращает полный HTML-документ с <link rel="stylesheet" href="styles.css">.
  // Заменяем этот тег на inline <style> — внешний файл недоступен в iframe.
  const iframeDoc = html.replace(
    /<link[^>]*href=["']styles\.css["'][^>]*\/?>/,
    `<style>${css}</style>`,
  )

  const copyHtml = async () => {
    await navigator.clipboard.writeText(html)
    setCopiedHtml(true)
    setTimeout(() => setCopiedHtml(false), 2000)
  }

  const copyCss = async () => {
    await navigator.clipboard.writeText(css)
    setCopiedCss(true)
    setTimeout(() => setCopiedCss(false), 2000)
  }

  return (
    <div className="w-[480px] bg-white border-l border-gray-200 flex flex-col h-full overflow-hidden">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 shrink-0">
        {(['preview', 'code'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-3 font-medium text-sm transition-colors ${
              activeTab === tab
                ? 'text-sky-600 border-b-2 border-sky-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'preview' ? 'Превью' : 'Код'}
          </button>
        ))}
        {/* Закрыть панель — scroll messages back */}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'preview' ? (
          // Iframe изолирован: стили основного приложения не протекают внутрь
          <iframe
            key={iframeDoc}
            srcDoc={iframeDoc}
            className="w-full h-full border-none"
            title="Превью компонента"
            sandbox="allow-same-origin"
          />
        ) : (
          <div className="h-full overflow-auto p-4 space-y-5">
            <section>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">HTML</h3>
              {/* whitespace-pre-wrap + overflow-x-auto: длинные строки переносятся, но при необходимости скроллятся */}
              <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-800
                              whitespace-pre-wrap break-all overflow-x-auto">
                <code>{html}</code>
              </pre>
            </section>
            <section>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">CSS</h3>
              <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-800
                              whitespace-pre-wrap break-all overflow-x-auto">
                <code>{css}</code>
              </pre>
            </section>
          </div>
        )}
      </div>

      {/* Copy actions */}
      <div className="border-t border-gray-200 p-3 flex gap-2 shrink-0">
        <button
          onClick={copyHtml}
          className={`flex-1 font-medium py-2 px-3 rounded-lg transition-colors text-sm ${
            copiedHtml
              ? 'bg-green-500 text-white'
              : 'bg-sky-600 hover:bg-sky-700 text-white'
          }`}
        >
          {copiedHtml ? '✓ Скопировано' : 'Копировать HTML'}
        </button>
        <button
          onClick={copyCss}
          className={`flex-1 font-medium py-2 px-3 rounded-lg transition-colors text-sm ${
            copiedCss
              ? 'bg-green-500 text-white'
              : 'bg-slate-600 hover:bg-slate-700 text-white'
          }`}
        >
          {copiedCss ? '✓ Скопировано' : 'Копировать CSS'}
        </button>
      </div>
    </div>
  )
}
