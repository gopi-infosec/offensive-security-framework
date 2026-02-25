// app/page.tsx
import ChatInterface from '@/components/ChatInterface'
import SidebarNav from '@/components/SidebarNav'

export default function Home() {
  return (
    <main className="flex h-screen overflow-hidden">
      {/* Animated gradient background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-600/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 right-0 w-96 h-96 bg-pink-600/5 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      {/* Sidebar Navigation */}
      <SidebarNav />

      {/* Main Chat Interface */}
      <ChatInterface />
    </main>
  )
}