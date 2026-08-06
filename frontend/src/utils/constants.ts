export const ROLE_OPTIONS = [
  'DevOps',
  'DevSecOps',
  'Desenvolvedor Backend',
  'Backend Python',
  'Backend .NET',
  'Cloud Engineer',
  'Platform Engineer',
  'Site Reliability Engineer',
  'Application Security',
  'Segurança da Informação',
  'Analista de Infraestrutura',
  'Suporte Cloud',
  'Desenvolvedor Full Stack',
]

export const LEVEL_OPTIONS = ['Estágio', 'Trainee', 'Júnior', 'Pleno', 'Sênior', 'Especialista', 'Lead', 'Staff', 'Principal', 'Manager']

export const TECH_OPTIONS = [
  'Python', 'C#', '.NET', 'Docker', 'Linux', 'GitHub Actions', 'GitLab CI',
  'Azure', 'AWS', 'Google Cloud', 'Cloudflare', 'Nginx', 'CI/CD', 'Terraform',
  'Kubernetes', 'PostgreSQL', 'MySQL', 'FastAPI', 'React', 'Next.js',
  'Segurança', 'OWASP',
]

export const DEFAULT_EXCLUDE_WORDS = [
  'Senior', 'Sênior', 'Sr', 'Staff', 'Lead', 'Principal', 'Manager',
  'Gerente', 'Especialista',
]

export const DAYS_OPTIONS = [
  { label: 'Últimas 24h', value: 1 },
  { label: 'Últimos 3 dias', value: 3 },
  { label: 'Últimos 7 dias', value: 7 },
  { label: 'Últimos 15 dias', value: 15 },
  { label: 'Últimos 30 dias', value: 30 },
  { label: 'Qualquer período', value: null },
]

export const LOCATION_MODE_OPTIONS = [
  { value: 'brasil', label: 'Brasil inteiro' },
  { value: 'estado', label: 'Por estado' },
  { value: 'cidade', label: 'Por cidade' },
  { value: 'remoto_brasil', label: 'Remoto no Brasil' },
  { value: 'remoto_latam', label: 'Remoto América Latina' },
  { value: 'remoto_global', label: 'Remoto global' },
  { value: 'internacional', label: 'Aceitar vagas internacionais' },
]

export const SOURCE_LABELS: Record<string, string> = {
  greenhouse: 'Greenhouse',
  lever: 'Lever',
  gupy: 'Gupy',
  github: 'GitHub',
  remotive: 'Remotive',
  manual_search: 'Pesquisa manual',
}

export const DEFAULT_FILTERS = {
  roles: [] as string[],
  role: null as string | null,
  levels: ['Júnior', 'Pleno'] as string[],
  technologies: [] as string[],
  min_skill_matches: 0,
  location: 'Brasil',
  location_mode: 'brasil',
  remote: false,
  days_ago: 7 as number | null,
  required_words: [] as string[],
  excluded_words: [] as string[],
  include_unlevel: true,
  accept_international: false,
  sources: [] as string[],
  max_results: 100,
}
