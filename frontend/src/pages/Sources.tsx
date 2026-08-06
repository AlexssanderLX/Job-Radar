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
  const load = () => api.getSources().then(setItems).catch((e) => setError(String(e)))
  useEffect(() => { void load() }, [])

  const remove = async (item: Source) => {
    if (!confirm(`Excluir a fonte "${item.display_name}"?`)) return
    try { await api.deleteSource(item.id); await load() }
    catch (e) { setError(e instanceof Error ? e.message : String(e)) }
  }

  return <div className="space-y-4 max-w-5xl">
    <PageHeader title="Fontes" description="Onde o Job Radar procura vagas" action={<Button size="sm" onClick={() => setEditing(null)}><Plus size={14}/>Adicionar fonte</Button>}/>
    {error && <p className="rounded-md border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">{error}</p>}
    <div className="grid gap-3 sm:grid-cols-2">{items.map((item) => <div key={item.id} className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0"><p className="font-medium text-zinc-100">{item.display_name}</p><p className="mt-1 truncate text-xs text-zinc-500">{item.domain || (item.is_manual ? 'Pesquisa externa' : 'Conector automático')}</p></div>
        <button onClick={() => { void api.updateSource(item.id, { active: !item.active }).then(load) }} className={item.active ? 'text-xs text-emerald-400' : 'text-xs text-zinc-500'}>{item.active ? 'Ativa' : 'Inativa'}</button>
      </div>
      <div className="mt-3 flex justify-end gap-1"><button aria-label={`Editar ${item.display_name}`} onClick={() => setEditing(item)} className="p-2 text-zinc-500 hover:text-zinc-200"><Pencil size={14}/></button><button aria-label={`Excluir ${item.display_name}`} onClick={() => void remove(item)} className="p-2 text-zinc-500 hover:text-red-400"><Trash2 size={14}/></button></div>
    </div>)}</div>
    {editing !== undefined && <SourceDialog item={editing} onClose={() => setEditing(undefined)} onSaved={() => { setEditing(undefined); void load() }}/>} 
  </div>
}

function SourceDialog({ item, onClose, onSaved }: { item: Source | null; onClose: () => void; onSaved: () => void }) {
  const [displayName, setDisplayName] = useState(item?.display_name ?? '')
  const [template, setTemplate] = useState(item?.search_url_template ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const applyLinkedIn = () => {
    setDisplayName('LinkedIn Jobs')
    setTemplate('https://www.linkedin.com/jobs/search/?keywords={query}')
  }

  const save = async () => {
    if (!displayName.trim()) return setError('Informe o nome da fonte.')
    if (!item && !template.trim()) return setError('Informe o link de pesquisa.')
    setSaving(true); setError('')
    try {
      let searchUrl = template.trim()
      if (searchUrl && !searchUrl.includes('{query}')) {
        const parsed = new URL(searchUrl)
        parsed.searchParams.set(parsed.hostname.includes('linkedin.com') ? 'keywords' : 'q', '{query}')
        searchUrl = parsed.toString().replace('%7Bquery%7D', '{query}')
      }
      const domain = searchUrl ? new URL(searchUrl.replace('{query}', 'vagas')).hostname : item?.domain ?? null
      const identifier = item?.name ?? displayName.trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')
      const data = {
        name: identifier,
        display_name: displayName.trim(),
        source_type: item?.source_type ?? 'manual',
        is_manual: item?.is_manual ?? true,
        active: item?.active ?? true,
        priority: item?.priority ?? 10,
        description: item?.description ?? null,
        domain,
        search_url_template: searchUrl || null,
      }
      if (item) await api.updateSource(item.id, data)
      else await api.createSource(data)
      onSaved()
    } catch (e) {
      setError(e instanceof TypeError ? 'Informe um link válido começando com https://.' : e instanceof Error ? e.message : String(e))
      setSaving(false)
    }
  }

  return <Dialog open onClose={onClose} title={item ? 'Editar fonte' : 'Adicionar fonte'}>
    <div className="space-y-4">
      {!item && <button type="button" onClick={applyLinkedIn} className="w-full rounded-md border border-indigo-800/60 bg-indigo-950/30 px-3 py-2 text-left text-sm text-indigo-300 hover:bg-indigo-950/60"><strong>Adicionar LinkedIn</strong><span className="block text-xs text-indigo-400/70">Preenche tudo automaticamente.</span></button>}
      <Input label="Nome" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="LinkedIn Jobs"/>
      <Input label="Link de pesquisa" value={template} onChange={(e) => setTemplate(e.target.value)} placeholder="https://site.com/pesquisa"/>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <div className="flex justify-end gap-2"><Button variant="outline" onClick={onClose}>Cancelar</Button><Button loading={saving} onClick={save}>Salvar</Button></div>
    </div>
  </Dialog>
}
