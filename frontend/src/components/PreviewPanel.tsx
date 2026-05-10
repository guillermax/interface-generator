import { useState } from 'react'
import { Message } from '../types'

interface PreviewPanelProps {
  message: Message
}

export default function PreviewPanel({ message }: PreviewPanelProps) {
  const [activeTab, setActiveTab] = useState<'code' | 'preview'>('code')
  
  if (!message.preview) {
    return null
  }

  const { html, css } = message.preview
  const iframeContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        ${css}
      </style>
    </head>
    <body>
      ${html}
    </body>
    </html>
  `

  return (
    <div className="w-1/2 bg-white border-l border-gray-200 flex flex-col">
      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('code')}
          className={`px-4 py-3 font-semibold text-sm transition ${
            activeTab === 'code'
              ? 'text-blue-500 border-b-2 border-blue-500'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Code
        </button>
        <button
          onClick={() => setActiveTab('preview')}
          className={`px-4 py-3 font-semibold text-sm transition ${
            activeTab === 'preview'
              ? 'text-blue-500 border-b-2 border-blue-500'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Preview
        </button>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'code' ? (
          <div className="h-full overflow-auto p-4">
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">HTML</h3>
              <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">
                <code className="text-gray-800">{html}</code>
              </pre>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">CSS</h3>
              <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">
                <code className="text-gray-800">{css}</code>
              </pre>
            </div>
          </div>
        ) : (
          <iframe
            srcDoc={iframeContent}
            className="w-full h-full border-none"
            title="preview"
          />
        )}
      </div>
      
      {/* Copy button */}
      <div className="border-t border-gray-200 p-4 flex gap-2">
        <button
          onClick={() => {
            navigator.clipboard.writeText(`<style>${css}</style>${html}`)
          }}
          className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          Copy HTML
        </button>
        <button
          onClick={() => {
            navigator.clipboard.writeText(css)
          }}
          className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          Copy CSS
        </button>
      </div>
    </div>
  )
}
