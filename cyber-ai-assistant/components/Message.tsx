// components/Message.tsx
'use client'

import ReactMarkdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight'
import remarkGfm from 'remark-gfm'
import CodeBlock from './CodeBlock'
import 'highlight.js/styles/atom-one-dark.css'

interface MessageProps {
  message: {
    role: 'user' | 'assistant'
    content: string
  }
}

export default function Message({ message }: MessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
      <div
        className={`max-w-2xl rounded-lg px-4 py-3 backdrop-blur transition-all ${
          isUser
            ? 'bg-gradient-to-r from-purple-600 to-cyan-600 text-white rounded-bl-lg shadow-lg shadow-purple-500/30'
            : 'bg-slate-900/60 border border-purple-500/20 text-slate-100 rounded-br-lg'
        }`}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed">{message.content}</p>
        ) : (
          <div className="prose prose-invert max-w-none prose-sm">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                code: ({ node, className, children, ...props }) => {
                  const match = /language-(\w+)/.exec(className || '')
                  const lang = match ? match[1] : 'text'
                  return (
                    <CodeBlock
                      language={lang}
                      code={String(children).replace(/\n$/, '')}
                    />
                  )
                },
                p: ({ children }) => (
                  <p className="text-slate-300 leading-relaxed mb-3">
                    {children}
                  </p>
                ),
                h1: ({ children }) => (
                  <h1 className="text-xl font-bold text-purple-400 mt-4 mb-2">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-lg font-bold text-cyan-400 mt-3 mb-2">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-base font-bold text-purple-300 mt-2 mb-1">
                    {children}
                  </h3>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside space-y-1 mb-3 text-slate-300">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside space-y-1 mb-3 text-slate-300">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="ml-2 text-slate-300">{children}</li>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-purple-500 pl-4 py-1 my-3 bg-slate-800/50 rounded text-slate-400 italic">
                    {children}
                  </blockquote>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto my-3">
                    <table className="w-full border-collapse border border-slate-700">
                      {children}
                    </table>
                  </div>
                ),
                td: ({ children }) => (
                  <td className="border border-slate-700 px-3 py-2 text-slate-300">
                    {children}
                  </td>
                ),
                th: ({ children }) => (
                  <th className="border border-slate-700 px-3 py-2 bg-slate-800 text-purple-300 font-bold">
                    {children}
                  </th>
                ),
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:text-cyan-300 underline transition-colors"
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}