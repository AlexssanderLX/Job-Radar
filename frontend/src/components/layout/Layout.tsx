import { useState, type ReactNode } from 'react'
import { Menu } from 'lucide-react'
import { Sidebar } from './Sidebar'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex w-full min-h-screen bg-[#09090b]">
      <Sidebar mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)} />
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        {/* Mobile header */}
        <div className="flex md:hidden items-center h-14 px-4 border-b border-zinc-800 bg-zinc-950 sticky top-0 z-40">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 text-zinc-400 hover:text-zinc-100"
          >
            <Menu size={20} />
          </button>
        </div>
        <main className="flex-1 p-5 md:p-8 xl:p-10 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
