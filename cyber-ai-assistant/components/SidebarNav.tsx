// components/SidebarNav.tsx
'use client'

import { useState } from 'react'
import { Menu, X, Shield, Bug, AlertTriangle, BookOpen, BarChart3, Settings } from 'lucide-react'

const navItems = [
  { icon: Shield, label: 'Web Security', description: 'XSS, CSRF, SSRF' },
  { icon: Bug, label: 'Malware', description: 'Detection & Analysis' },
  { icon: AlertTriangle, label: 'Vulnerabilities', description: 'CVE Research' },
  { icon: BookOpen, label: 'OWASP Top 10', description: 'Security Risks' },
  { icon: BarChart3, label: 'Best Practices', description: 'Security Standards' },
  { icon: Settings, label: 'Incident Response', description: 'Crisis Management' },
]

export default function SidebarNav() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Mobile Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 md:hidden p-2 rounded-lg bg-purple-600 hover:bg-purple-700 transition-colors"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed md:relative top-0 left-0 h-screen w-64 bg-slate-900/80 backdrop-blur-xl border-r border-purple-500/20 transform transition-transform md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } z-40 flex flex-col`}
      >
        {/* Sidebar Header */}
        <div className="p-6 border-b border-purple-500/20">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-600 to-cyan-600 flex items-center justify-center text-xl font-bold">
              🛡️
            </div>
            <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              CyberGuard
            </h2>
          </div>
          <p className="text-xs text-slate-400">AI Security Assistant</p>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.label}
                onClick={() => setIsOpen(false)}
                className="w-full text-left px-4 py-3 rounded-lg hover:bg-purple-600/20 transition-all group border border-transparent hover:border-purple-500/30"
              >
                <div className="flex items-center gap-3">
                  <Icon
                    size={20}
                    className="text-purple-400 group-hover:text-cyan-400 transition-colors"
                  />
                  <div>
                    <p className="text-sm font-semibold text-slate-200 group-hover:text-purple-300">
                      {item.label}
                    </p>
                    <p className="text-xs text-slate-500 group-hover:text-slate-400">
                      {item.description}
                    </p>
                  </div>
                </div>
              </button>
            )
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-purple-500/20">
          <div className="p-4 rounded-lg bg-gradient-to-br from-purple-600/20 to-cyan-600/20 border border-purple-500/30">
            <p className="text-xs text-slate-300 mb-3">
              💡 <strong>Pro Tip:</strong> Ask specific questions for better security guidance.
            </p>
            <div className="flex gap-2">
              <button className="flex-1 px-3 py-1.5 text-xs rounded bg-purple-600/50 hover:bg-purple-600 text-white transition-colors">
                Examples
              </button>
              <button className="flex-1 px-3 py-1.5 text-xs rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition-colors">
                Docs
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 md:hidden z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  )
}