interface Props {
  score: number
}

export function ScoreBadge({ score }: Props) {
  const label =
    score >= 70 ? 'Alta' : score >= 40 ? 'Média' : score > 0 ? 'Baixa' : '–'

  const cls =
    score >= 70
      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      : score >= 40
      ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${cls}`}
      title={`Pontuação: ${score}`}
      aria-label={`Compatibilidade ${label}, ${score} pontos`}
    >
      {score > 0 ? score.toFixed(0) : '–'} <span aria-hidden>•</span> {label}
    </span>
  )
}
