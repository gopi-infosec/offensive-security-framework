// components/CodeBlock.tsx
'use client'

import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { Highlight, themes } from 'prism-react-renderer'

interface CodeBlockProps {
  language: string
  code: string
}

export default function CodeBlock({ language, code }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Highlight theme={themes.oneDark} code={code} language={language as any}>
      {({ className, style, tokens, getLineProps, getTokenProps }) => (
        <div className="relative my-3 rounded-lg overflow-hidden border border-slate-700/50">
          {/* Header */}
          <div className="flex justify-between items-center px-4 py-2 bg-slate-900/80 border-b border-slate-700/50">
            <span className="text-xs font-semibold text-slate-400 uppercase">
              {language}
            </span>
            <button
              onClick={handleCopy}
              className="p-1.5 rounded hover:bg-slate-800 transition-colors text-slate-400 hover:text-slate-200"
              title="Copy code"
            >
              {copied ? (
                <Check size={16} className="text-green-400" />
              ) : (
                <Copy size={16} />
              )}
            </button>
          </div>

          {/* Code */}
          <pre
            className={`${className} !bg-slate-950 !p-4 !m-0 overflow-x-auto text-sm`}
            style={style}
          >
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line, key: i })}>
                <span className="text-slate-500 inline-block w-8 text-right mr-4 select-none">
                  {i + 1}
                </span>
                {line.map((token, key) => (
                  <span key={key} {...getTokenProps({ token, key })} />
                ))}
              </div>
            ))}
          </pre>
        </div>
      )}
    </Highlight>
  )
}