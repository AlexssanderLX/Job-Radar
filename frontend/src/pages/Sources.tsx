import { useEffect, useState } from 'react'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import { api } from '../services/api'
import type { Source } from '../types'
import { Button } from '../components/ui/Button'
import { Dialog } from '../components/ui/Dialog'
import { Input } from '../components/ui/Input'
import { PageHeader } from '../components/ui/PageHeader'

export default function SourcesPage() {
  const [items, setItems] = useState<Source[]>([])
  const [editing, setEditing] = useState<Source | null | undefined>()
  const [error, setError] = useState('')
  const load = () => { api.getSources().then(setItems).catch((e) => setError(String(e))) }
  useEffect(load, [])
  const remove = async (item: Source) => {
    if (!confirm(`Excluir a fonte "${item.display_name}"?`)) return
    try { await api.deleteSource(item.id); load() }
    catch (e) { setError(e instanceof Error ? e.message : String(e)) }
  }
  return <div className="space-y-4 max-w-5xl">
    <PageHeader title="Fontes" description="Conectores e pesquisas externas configuráveis" action={<Button size="sm" onClick={() => setEditing(null)}><Plus size={14}/>Adicionar fonte</Button>}/>
    {error && <p className="rounded-md border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">{error}</p>}
    <div className="grid gap-3 sm:grid-cols-2">{items.map((item) => <div key={item.id} className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-4">
      <div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="font-medium text-zinc-100">{item.display_name}</p><p className="mt-1 text-xs text-zinc-500">{item.source_type} · prioridade {item.priority}{item.domain ? ` · ${item.domain}` : ''}</p></div><button onClick={() => { void api.updateSource(item.id, { active: !item.active }).then(load) }} className={item.active ? 'text-xs text-emerald-400' : 'text-xs text-zinc-500'}>{item.active ? 'Ativa' : 'Inativa'}</button></div>
      {item.description && <p className="mt-3 line-clamp-2 text-xs text-zinc-500">{item.description}</p>}
      {item.search_url_template && <p className="mt-2 truncate rounded bg-zinc-950 px-2 py-1 font-mono text-[10px] text-zinc-600">{item.search_url_template}</p>}
      {item.last_error && <p className="mt-2 text-xs text-red-400">{item.last_error}</p>}
      <div className="mt-3 flex justify-end gap-1"><button aria-label={`Editar ${item.display_name}`} onClick={() => setEditing(item)} className="p-2 text-zinc-500 hover:text-zinc-200"><Pencil size={14}/></button><button aria-label={`Excluir ${item.display_name}`} onClick={() => void remove(item)} className="p-2 text-zinc-500 hover:text-red-400"><Trash2 size={14}/></button></div>
    </div>)}</div>
    {editing !== undefined && <SourceDialog item={editing} onClose={() => setEditing(undefined)} onSaved={() => { setEditing(undefined); load() }}/>} 
  </div>
}

function SourceDialog({ item, onClose, onSaved }: { item: Source | null; onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState(item?.name ?? '')
  const [displayName, setDisplayName] = useState(item?.display_name ?? '')
  const [sourceType, setSourceType] = useState(item?.source_type ?? 'manual')
  const [domain, setDomain] = useState(item?.domain ?? '')
  const [template, setTemplate] = useState(item?.search_url_template ?? '')
  const [description, setDescription] = useState(item?.description ?? '')
  const [priority, setPriority] = useState(item?.priority ?? 10)
  const [active, setActive] = useState(item?.active ?? true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const applyLinkedIn = () => {
    setName('linkedin'); setDisplayName('LinkedIn Jobs'); setSourceType('manual')
    setDomain('linkedin.com'); setTemplate('https://www.linkedin.com/jobs/search/?keywords={query}')
    setDescription('Pesquisa pública manual no LinkedIn Jobs, sem login ou automação.')
  }
  const save = async () => {
    if (!name.trim() || !displayName.trim()) return setError('Informe o identificador e o nome da fonte.')
    if (sourceType === 'manual' && !template.includes('{query}')) return setError('A URL de pesquisa deve conter {query}.')
    setSaving(true); setError('')
    const data = {
      name: name.trim().toLowerCase().replace(/[^a-z0-9_-]+/g, '_'), display_name: displayName.trim(),
      source_type: sourceType, is_manual: sourceType === 'manual', active, priority,
      description: description || null, domain: domain || null, search_url_template: template || null,
    }
    try {
      if (item) await api.updateSource(item.id, data)
      else await api.createSource(data)
      onSaved()
    } catch (e) { setError(e instanceof Error ? e.message : String(e)); setSaving(false) }
  }
  return <Dialog open onClose={onClose} title={item ? 'Editar fonte' : 'Adicionar fonte'}>
    <div className="space-y-4">
      {!item && <button type="button" onClick={applyLinkedIn} className="w-full rounded-md border border-indigo-800/60 bg-indigo-950/30 px-3 py-2 text-left text-sm text-indigo-300 hover:bg-indigo-950/60"><strong>Usar modelo do LinkedIn</strong><span className="block text-xs text-indigo-400/70">Preenche uma pesquisa pública e manual segura.</span></button>}
      <div className="grid gap-3 sm:grid-cols-2"><Input label="Identificador" value={name} disabled={Boolean(item)} onChange={(e) => setName(e.target.value)} placeholder="linkedin"/><Input label="Nome de exibição" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="LinkedIn Jobs"/></div>
      <div className="grid gap-3 sm:grid-cols-2"><label className="flex flex-col gap-1 text-xs font-medium text-zinc-400">Tipo<select value={sourceType} onChange={(e) => setSourceType(e.target.value)} className="h-9 rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-zinc-100"><option value="manual">Pesquisa manual</option><option value="web_search">Pesquisa web</option><option value="rss">RSS</option><option value="career_page">Página de carreira</option><option value="api">API pública</option></select></label><Input label="Prioridade" type="number" value={priority} onChange={(e) => setPriority(Number(e.target.value))}/></div>
      <Input label="Domínio" value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="linkedin.com"/>
      <Input label="URL de pesquisa" value={template} onChange={(e) => setTemplate(e.target.value)} placeholder="https://site.com/search?q={query}"/>
      <p className="-mt-2 text-xs text-zinc-600">Use <code>{'{query}'}</code> onde os cargos e filtros devem ser inseridos.</p>
      <Input label="Descrição" value={description} onChange={(e) => setDescription(e.target.value)}/>
      <label className="flex items-center gap-2 text-sm text-zinc-300"><input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)}/>Fonte ativa</label>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <div className="flex justify-end gap-2"><Button variant="outline" onClick={onClose}>Cancelar</Button><Button loading={saving} onClick={save}>Salvar fonte</Button></div>
    </div>
  </Dialog>
}
