// components/LoadingSpinner.tsx
'use client'

export default function LoadingSpinner() {
  return (
    <div className="flex items-center gap-3 p-4 rounded-lg bg-slate-900/60 border border-purple-500/20 backdrop-blur animate-fadeIn">
      {/* Animated spinning circles */}
      <div className="relative w-8 h-8 flex items-center justify-center">
        {/* Outer ring */}
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-purple-500 border-r-cyan-500 animate-spin"></div>
        
        {/* Inner ring */}
        <div className="absolute inset-2 rounded-full border-2 border-transparent border-t-cyan-500 animate-spin" style={{ animationDirection: 'reverse' }}></div>
        
        {/* Center glow */}
        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 animate-pulse"></div>
      </div>

      <span className="text-sm text-slate-300 font-semibold">
        🔍 Analyzing your question...
      </span>
    </div>
  )
}