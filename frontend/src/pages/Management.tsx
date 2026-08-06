import { useCallback, useEffect, useMemo, useState } from 'react'
import { Archive, Pencil, Play, Plus, Search, Trash2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import type { Role, SearchHistory, SearchProfile, Skill, Source, Stack } from '../types'
import { Button } from '../components/ui/Button'
import { Dialog } from '../components/ui/Dialog'
import { EmptyState } from '../components/ui/EmptyState'
import { Input } from '../components/ui/Input'
import { PageHeader } from '../components/ui/PageHeader'
import { TagInput } from '../components/ui/TagInput'

type CatalogKind = 'roles' | 'skills'
type CatalogItem = Role | Skill

export function CatalogPage({ kind }: { kind: CatalogKind }) {
  const [items, setItems] = useState<CatalogItem[]>([])
  const [query, setQuery] = useState('')
  const [editing, setEditing] = useState<CatalogItem | null | undefined>()
  const [error, setError] = useState('')
  const title = kind === 'roles' ? 'Cargos' : 'Habilidades'
  const load = useCallback(() => {
    const request = kind === 'roles' ? api.getRoles() : api.getSkills()
    request.then(setItems).catch((e) => setError(String(e)))
  }, [kind])
  useEffect(load, [load])
  const shown = items.filter((item) => item.name.toLowerCase().includes(query.toLowerCase()))
  const remove = async (item: CatalogItem) => {
    if (!confirm(`Excluir "${item.name}"? Itens usados por perfis não podem ser removidos.`)) return
    try {
      if (kind === 'roles') await api.deleteRole(item.id)
      else await api.deleteSkill(item.id)
      load()
    } catch (e) { setError(e instanceof Error ? e.message : String(e)) }
  }
  return <div className="space-y-4 max-w-5xl">
    <PageHeader title={title} description={`Catálogo configurável · ${items.length} itens`} action={<Button size="sm" onClick={() => setEditing(null)}><Plus size={14}/>Adicionar</Button>} />
    <div className="relative max-w-sm"><Search size={15} className="absolute left-3 top-2.5 text-zinc-500"/><input aria-label={`Pesquisar ${title}`} value={query} onChange={(e) => setQuery(e.target.value)} className="h-9 w-full rounded-md border border-zinc-700 bg-zinc-900 pl-9 pr-3 text-sm" placeholder="Pesquisar por nome…"/></div>
    {error && <p className="rounded-md border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">{error}</p>}
    <div className="overflow-hidden rounded-lg border border-zinc-800">
      {shown.map((item) => <div key={item.id} className="flex items-center gap-3 border-b border-zinc-800 px-4 py-3 last:border-0">
        <div className="min-w-0 flex-1"><p className="text-sm font-medium text-zinc-100">{item.name}</p><p className="truncate text-xs text-zinc-500">{item.category || 'Sem categoria'}{item.aliases.length ? ` · ${item.aliases.join(', ')}` : ''}</p></div>
        <span className={item.active ? 'text-xs text-emerald-400' : 'text-xs text-zinc-600'}>{item.active ? 'Ativo' : 'Arquivado'}</span>
        <button aria-label={`Editar ${item.name}`} onClick={() => setEditing(item)} className="p-2 text-zinc-400 hover:text-white"><Pencil size={14}/></button>
        <button aria-label={`Excluir ${item.name}`} onClick={() => remove(item)} className="p-2 text-zinc-500 hover:text-red-400"><Trash2 size={14}/></button>
      </div>)}
      {!shown.length && <EmptyState title="Nenhum item encontrado" description="Adicione um item ou ajuste a pesquisa."/>}
    </div>
    {editing !== undefined && <CatalogDialog kind={kind} item={editing} onClose={() => setEditing(undefined)} onSaved={() => { setEditing(undefined); load() }}/>}
  </div>
}

function CatalogDialog({ kind, item, onClose, onSaved }: { kind: CatalogKind; item: CatalogItem | null; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState(item?.name ?? '')
  const [category, setCategory] = useState(item?.category ?? '')
  const [description, setDescription] = useState(item?.description ?? '')
  const [aliases, setAliases] = useState(item?.aliases ?? [])
  const [active, setActive] = useState(item?.active ?? true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const save = async () => {
    if (!name.trim()) return setError('Informe um nome.')
    setSaving(true)
    try {
      const base = { name: name.trim(), category: category || null, description: description || null, aliases, active }
      if (kind === 'roles') {
        const data = { ...base, excluded_words: item && 'excluded_words' in item ? item.excluded_words : [] }
        if (item) await api.updateRole(item.id, data)
        else await api.createRole(data)
      } else if (item) await api.updateSkill(item.id, base)
      else await api.createSkill(base)
      onSaved()
    } catch (e) { setError(e instanceof Error ? e.message : String(e)); setSaving(false) }
  }
  return <Dialog open onClose={onClose} title={`${item ? 'Editar' : 'Adicionar'} ${kind === 'roles' ? 'cargo' : 'habilidade'}`}>
    <div className="space-y-4"><Input label="Nome" value={name} onChange={(e) => setName(e.target.value)}/><Input label="Categoria" value={category} onChange={(e) => setCategory(e.target.value)}/><Input label="Descrição" value={description} onChange={(e) => setDescription(e.target.value)}/><TagInput label="Aliases" value={aliases} onChange={setAliases} placeholder="Digite e pressione Enter"/>
      <label className="flex gap-2 text-sm text-zinc-300"><input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)}/>Ativo</label>
      {error && <p className="text-sm text-red-400">{error}</p>}<div className="flex justify-end gap-2"><Button variant="outline" onClick={onClose}>Cancelar</Button><Button loading={saving} onClick={save}>Salvar</Button></div>
    </div>
  </Dialog>
}

function SimpleList<T extends { id: number; name: string; active: boolean }>({ title, description, items, onArchive }: { title: string; description: string; items: T[]; onArchive: (item: T) => void }) {
  return <div className="space-y-4 max-w-5xl"><PageHeader title={title} description={description}/><div className="overflow-hidden rounded-lg border border-zinc-800">{items.map((item) => <div key={item.id} className="flex items-center gap-3 border-b border-zinc-800 px-4 py-3 last:border-0"><span className="flex-1 text-sm text-zinc-100">{item.name}</span><span className={item.active ? 'text-xs text-emerald-400' : 'text-xs text-zinc-600'}>{item.active ? 'Ativo' : 'Inativo'}</span><button onClick={() => onArchive(item)} className="p-2 text-zinc-500 hover:text-zinc-200" aria-label={`Alterar estado de ${item.name}`}><Archive size={14}/></button></div>)}{!items.length && <EmptyState title="Nenhum registro" description="Os registros criados aparecerão aqui."/>}</div></div>
}

export function StacksPage() {
  const [items, setItems] = useState<Stack[]>([])
  const load = () => { api.getStacks().then(setItems).catch(() => {}) }
  useEffect(load, [])
  return <SimpleList title="Stacks" description="Grupos reutilizáveis de habilidades" items={items} onArchive={(item) => { void api.updateStack(item.id, { active: !item.active }).then(load) }}/>
}

export function SourcesPage() {
  const [items, setItems] = useState<Source[]>([])
  const load = () => { api.getSources().then(setItems).catch(() => {}) }
  useEffect(load, [])
  return <div className="space-y-4 max-w-5xl"><PageHeader title="Fontes" description="Conectores e pesquisas externas"/><div className="grid gap-3 sm:grid-cols-2">{items.map((item) => <div key={item.id} className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-4"><div className="flex justify-between"><p className="font-medium text-zinc-100">{item.display_name}</p><button onClick={() => { void api.updateSource(item.id, { active: !item.active }).then(load) }} className={item.active ? 'text-xs text-emerald-400' : 'text-xs text-zinc-500'}>{item.active ? 'Ativa' : 'Inativa'}</button></div><p className="mt-1 text-xs text-zinc-500">{item.source_type} · prioridade {item.priority}</p>{item.last_error && <p className="mt-2 text-xs text-red-400">{item.last_error}</p>}</div>)}</div></div>
}

export function ProfilesPage() {
  const [items, setItems] = useState<SearchProfile[]>([])
  const navigate = useNavigate()
  useEffect(() => { api.getProfiles().then(setItems).catch(() => {}) }, [])
  return <div className="space-y-4 max-w-5xl"><PageHeader title="Perfis de busca" description="Configurações reutilizáveis"/><div className="grid gap-3 sm:grid-cols-2">{items.map((item) => <div key={item.id} className="rounded-lg border border-zinc-800 p-4"><p className="font-medium text-zinc-100">{item.name}</p><p className="mt-1 text-xs text-zinc-500">{item.roles.join(', ') || 'Sem cargos'} · {item.strategy}</p><Button className="mt-3" size="sm" onClick={() => navigate(`/search?roles=${encodeURIComponent(JSON.stringify(item.roles))}`)}><Play size={13}/>Carregar</Button></div>)}{!items.length && <EmptyState title="Nenhum perfil" description="Salve filtros de busca para reutilizá-los."/ >}</div></div>
}

export function HistoryPage() {
  const [items, setItems] = useState<SearchHistory[]>([])
  useEffect(() => { api.getSearchHistory().then(setItems).catch(() => {}) }, [])
  const total = useMemo(() => items.reduce((sum, item) => sum + item.total_found, 0), [items])
  return <div className="space-y-4 max-w-5xl"><PageHeader title="Histórico" description={`${items.length} pesquisas · ${total} resultados`}/><div className="overflow-hidden rounded-lg border border-zinc-800">{items.map((item) => <div key={item.id} className="flex items-center gap-3 border-b border-zinc-800 px-4 py-3 last:border-0"><Search size={14} className="text-zinc-500"/><div className="flex-1"><p className="text-sm text-zinc-200">{item.total_found} resultados nesta busca</p><p className="text-xs text-zinc-500">{new Date(item.searched_at).toLocaleString('pt-BR')} · {item.duration_seconds.toFixed(1)}s</p></div>{item.sources_failed.length > 0 && <span className="text-xs text-amber-400">{item.sources_failed.length} falha(s)</span>}</div>)}{!items.length && <EmptyState title="Sem histórico" description="As pesquisas executadas aparecerão aqui."/ >}</div></div>
}
