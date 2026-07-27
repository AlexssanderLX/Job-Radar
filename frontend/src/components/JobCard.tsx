import { ExternalLink, Heart, EyeOff, Copy, CheckCircle2, MapPin, Building2, Calendar, Zap } from 'lucide-react'
import { useState } from 'react'
import type { Job } from '../types'
import { ScoreBadge } from './ScoreBadge'
import { SOURCE_LABELS } from '../utils/constants'

interface Props {
  job: Job
  onFavorite: (id: number, current: boolean) => void
  onHide: (id: number) => void
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return '—'
  }
}

function ModalityBadge({ modality }: { modality: string | null }) {
  if (!modality) return null
  const m = modality.toLowerCase()
  if (m === 'remote' || m === 'remoto') {
    return (
      <span className="text-xs bg-teal-100 dark:bg-teal-900 text-teal-700 dark:text-teal-200 px-1.5 py-0.5 rounded">
        Remoto
      </span>
    )
  }
  if (m === 'hybrid' || m === 'híbrido') {
    return (
      <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 px-1.5 py-0.5 rounded">
        Híbrido
      </span>
    )
  }
  if (m === 'on-site' || m === 'presencial') {
    return (
      <span className="text-xs bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-200 px-1.5 py-0.5 rounded">
        Presencial
      </span>
    )
  }
  return null
}

function applyTarget(source: string): string {
  if (source === 'greenhouse') return 'Greenhouse'
  if (source === 'lever') return 'Lever'
  if (source === 'gupy') return 'Gupy'
  if (source === 'github') return 'GitHub'
  return SOURCE_LABELS[source] ?? source
}

export function JobCard({ job, onFavorite, onHide }: Props) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(job.apply_url).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  if (job.is_manual) {
    return (
      <div className="border border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-800/50">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 px-2 py-0.5 rounded font-medium">
                Pesquisa manual
              </span>
              <span className="text-xs text-gray-500">{SOURCE_LABELS[job.source] ?? job.source}</span>
            </div>
            <h3 className="font-medium text-gray-900 dark:text-gray-100 text-sm leading-snug">{job.title}</h3>
            {job.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{job.description}</p>
            )}
          </div>
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 flex items-center gap-1 px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <ExternalLink size={12} />
            Abrir pesquisa
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className={`border rounded-lg p-4 bg-white dark:bg-gray-800 transition-all ${
      job.match_score >= 70
        ? 'border-green-200 dark:border-green-800'
        : job.match_score >= 40
        ? 'border-yellow-200 dark:border-yellow-800'
        : 'border-gray-200 dark:border-gray-700'
    }`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex flex-wrap items-center gap-1.5 mb-1.5">
            <ScoreBadge score={job.match_score} />
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {SOURCE_LABELS[job.source] ?? job.source}
            </span>
            {job.level && (
              <span className="text-xs bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-200 px-1.5 py-0.5 rounded">
                {job.level}
              </span>
            )}
            <ModalityBadge modality={job.modality} />
          </div>

          {/* Title */}
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm leading-snug mb-1">
            {job.title}
          </h3>

          {/* Meta */}
          <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-xs text-gray-500 dark:text-gray-400 mb-2">
            <span className="flex items-center gap-1">
              <Building2 size={11} />
              {job.company}
            </span>
            {job.location && (
              <span className="flex items-center gap-1">
                <MapPin size={11} />
                {job.location}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Calendar size={11} />
              {formatDate(job.published_at)}
            </span>
          </div>

          {/* Technologies */}
          {job.technologies.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {job.technologies.slice(0, 8).map((t) => (
                <span
                  key={t}
                  className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded"
                >
                  {t}
                </span>
              ))}
            </div>
          )}

          {/* Match summary */}
          {job.match_summary && (
            <p className="text-xs text-gray-500 dark:text-gray-400 flex items-start gap-1">
              <Zap size={11} className="shrink-0 mt-0.5" />
              {job.match_summary}
            </p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
        <a
          href={job.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          title={`Candidatar-se em ${applyTarget(job.source)}`}
          className="flex items-center gap-1 px-3 py-1.5 text-xs bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
        >
          <ExternalLink size={12} />
          Ver vaga — {applyTarget(job.source)}
        </a>

        <button
          onClick={() => onFavorite(job.id, job.is_favorite)}
          className={`flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-md border transition-colors ${
            job.is_favorite
              ? 'bg-pink-50 border-pink-300 text-pink-600 dark:bg-pink-900/30 dark:border-pink-700 dark:text-pink-300'
              : 'border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:border-pink-300 hover:text-pink-600'
          }`}
          aria-label={job.is_favorite ? 'Remover dos favoritos' : 'Favoritar'}
        >
          <Heart size={12} className={job.is_favorite ? 'fill-current' : ''} />
          {job.is_favorite ? 'Favoritado' : 'Favoritar'}
        </button>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-md border border-gray-200 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:border-gray-400 transition-colors"
          aria-label="Copiar link"
        >
          {copied ? <CheckCircle2 size={12} /> : <Copy size={12} />}
          {copied ? 'Copiado' : 'Copiar'}
        </button>

        <button
          onClick={() => onHide(job.id)}
          className="ml-auto flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-md border border-gray-200 dark:border-gray-600 text-gray-400 hover:text-gray-600 hover:border-gray-400 transition-colors"
          aria-label="Ocultar vaga"
        >
          <EyeOff size={12} />
          Ocultar
        </button>
      </div>
    </div>
  )
}
