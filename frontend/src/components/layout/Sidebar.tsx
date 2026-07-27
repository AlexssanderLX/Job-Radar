import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Search, Briefcase, BookMarked, Tag, Zap, Globe,
  History, Layers3, ChevronLeft, ChevronRight, Radar,
} from 'lucide-react'

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/search', label: 'Pesquisar', icon: Search },
  { path: '/jobs', label: 'Vagas', icon: Briefcase },
  { path: '/profiles', label: 'Perfis', icon: BookMarked },
  { path: '/roles', label: 'Cargos', icon: Tag },
  { path: '/skills', label: 'Habilidades', icon: Zap },
  { path: '/stacks', label: 'Stacks', icon: Layers3 },
  { path: '/sources', label: 'Fontes', icon: Globe },
  { path: '/history', label: 'Histórico', icon: History },
]

interface SidebarProps {
  mobileOpen: boolean
  onMobileClose: () => void
}

export function Sidebar({ mobileOpen, onMobileClose }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()

  const sidebarContent = (
    <div
      className={[
        'flex flex-col h-full bg-zinc-950 border-r border-zinc-800 transition-all duration-200',
        collapsed ? 'w-16' : 'w-60',
      ].join(' ')}
    >
      {/* Logo */}
      <div className={['flex items-center h-14 border-b border-zinc-800 shrink-0', collapsed ? 'justify-center px-2' : 'px-4 gap-3'].join(' ')}>
        <Radar size={20} className="text-indigo-400 shrink-0" />
        {!collapsed && (
          <div className="flex items-center gap-2 min-w-0">
            <span className="font-bold text-zinc-100 text-sm tracking-tight truncate">Job Radar</span>
            <span className="text-xs px-1.5 py-0.5 bg-green-900/60 text-green-400 rounded text-[10px] border border-green-800/50">local</span>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
          const isActive = path === '/'
            ? location.pathname === '/'
            : location.pathname.startsWith(path)
          return (
            <NavLink
              key={path}
              to={path}
              onClick={onMobileClose}
              title={collapsed ? label : undefined}
              className={[
                'flex items-center rounded-md text-sm font-medium transition-colors group relative',
                collapsed ? 'h-10 w-10 justify-center mx-auto' : 'h-9 px-2.5 gap-2.5',
                isActive
                  ? 'bg-indigo-600/20 text-indigo-400'
                  : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100',
              ].join(' ')}
            >
              <Icon size={16} className="shrink-0" />
              {!collapsed && <span>{label}</span>}
              {collapsed && (
                <span className="absolute left-full ml-2 px-2 py-1 bg-zinc-800 text-zinc-100 text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none z-50 border border-zinc-700 shadow-lg">
                  {label}
                </span>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Collapse toggle (desktop only) */}
      <div className="shrink-0 border-t border-zinc-800 p-2">
        <button
          onClick={() => setCollapsed((v) => !v)}
          className={[
            'flex items-center justify-center h-9 w-full rounded-md text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 transition-colors',
          ].join(' ')}
          title={collapsed ? 'Expandir' : 'Recolher'}
        >
          {collapsed ? <ChevronRight size={16} /> : <><ChevronLeft size={16} /><span className="ml-2 text-xs">Recolher</span></>}
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex h-screen sticky top-0 shrink-0">
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={onMobileClose} />
          <div className="relative h-full">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  )
}
