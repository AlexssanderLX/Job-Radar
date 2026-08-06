"""
Query expansion configuration.
Maps canonical terms to search variants used when querying sources.
"""

ROLE_EXPANSIONS: dict[str, list[str]] = {
    "devops": [
        "DevOps", "DevOps Engineer", "Analista DevOps", "Cloud Engineer",
        "Platform Engineer", "Infrastructure Engineer", "SRE",
        "Site Reliability Engineer", "DevSecOps",
    ],
    "devsecops": [
        "DevSecOps", "DevSecOps Engineer", "Security Engineer DevOps",
        "Platform Security Engineer",
    ],
    "backend": [
        "Backend Developer", "Desenvolvedor Backend", "Back-end Developer",
        "Software Engineer", "Software Developer",
    ],
    "backend python": [
        "Python Developer", "Backend Python", "Python Engineer",
        "Software Engineer Python", "Desenvolvedor Python",
    ],
    "backend .net": [
        ".NET Developer", "Backend .NET", "C# Developer",
        "Software Engineer .NET", "Desenvolvedor .NET",
    ],
    "cloud engineer": [
        "Cloud Engineer", "Cloud Architect", "AWS Engineer",
        "Azure Engineer", "GCP Engineer", "Cloud Infrastructure",
    ],
    "platform engineer": [
        "Platform Engineer", "Infrastructure Engineer", "DevOps",
        "SRE", "Cloud Platform Engineer",
    ],
    "sre": [
        "SRE", "Site Reliability Engineer", "Platform Engineer",
        "DevOps Engineer", "Infrastructure Engineer",
    ],
    "site reliability engineer": [
        "SRE", "Site Reliability Engineer", "Platform Engineer",
        "DevOps Engineer", "Infrastructure Engineer",
    ],
    "application security": [
        "Application Security", "AppSec Engineer", "Security Engineer",
        "Penetration Tester", "SAST DAST", "Segurança de Aplicações",
    ],
    "segurança da informação": [
        "Segurança da Informação", "Information Security", "InfoSec",
        "Analista de Segurança", "Cybersecurity Analyst",
    ],
    "analista de infraestrutura": [
        "Analista de Infraestrutura", "Infrastructure Analyst",
        "Sysadmin", "Administrador de Sistemas",
    ],
    "suporte cloud": [
        "Suporte Cloud", "Cloud Support", "Cloud Operations",
        "Analista de Suporte Cloud",
    ],
    "desenvolvedor full stack": [
        "Full Stack Developer", "Desenvolvedor Full Stack",
        "Fullstack Engineer", "Full-Stack Developer",
    ],
    "full stack": [
        "Full Stack Developer", "Desenvolvedor Full Stack",
        "Fullstack Engineer", "Full-Stack Developer",
    ],
}

ROLE_KEYWORDS: dict[str, list[str]] = {
    "backend": ["backend", "back-end", "server-side", "software developer", "software engineer"],
    "backend .net": [".net", "c#", "backend", "back-end", "software developer", "software engineer"],
    "desenvolvedor backend": ["backend", "back-end", "server-side", "software developer", "software engineer"],
    "desenvolvedor full stack": ["full stack", "full-stack", "fullstack"],
    "full stack": ["full stack", "full-stack", "fullstack"],
}


def matches_role_text(text: str, roles: list[str]) -> bool:
    """Match job text using expansions plus safe role-family keywords."""
    lowered = text.lower()
    variants = expand_roles_multi(roles) or roles
    if any(variant.lower() in lowered for variant in variants):
        return True
    return any(
        keyword in lowered
        for role in roles
        for keyword in ROLE_KEYWORDS.get(role.strip().lower(), [])
    )

LEVEL_EXPANSIONS: dict[str, list[str]] = {
    "estágio": [
        "Estágio", "Estagiário", "Estagiária", "Intern", "Internship",
        "Estágio Técnico", "Programa de Estágio",
    ],
    "trainee": [
        "Trainee", "Programa Trainee", "Graduate Program",
        "Programa de Formação", "Graduate Trainee",
    ],
    "júnior": [
        "Júnior", "Junior", "Jr", "Jr.", "Entry Level", "Entry-Level",
        "Associate", "Iniciante", "Nível Inicial", "Nível I", "Nível 1",
        "Analista I", "Desenvolvedor I", "Desenvolvedor Júnior", "Analista Júnior",
    ],
    "pleno": [
        "Pleno", "Mid", "Mid-Level", "Middle", "Intermediário",
        "Nível II", "Nível 2", "Analista II", "Desenvolvedor II",
        "Analista Pleno", "Desenvolvedor Pleno",
    ],
    "sênior": ["Sênior", "Senior", "Sr", "Sr.", "Senior-Level", "Nível III", "Analista III"],
    "especialista": ["Especialista", "Specialist", "Expert"],
    "lead": ["Lead", "Tech Lead", "Team Lead", "Lead Engineer", "Lead Developer"],
    "staff": ["Staff", "Staff Engineer", "Senior Staff"],
    "principal": ["Principal", "Principal Engineer", "Principal Developer"],
    "manager": ["Manager", "Engineering Manager", "Gerente", "Gestor"],
}


def detect_level(text: str) -> str | None:
    padded = f" {text.lower()} "
    ordered = ["manager", "principal", "staff", "lead", "especialista", "sênior", "pleno", "júnior", "trainee", "estágio"]
    canonical = {
        "manager": "Manager", "principal": "Principal", "staff": "Staff", "lead": "Lead",
        "especialista": "Especialista", "sênior": "Sênior", "pleno": "Pleno",
        "júnior": "Júnior", "trainee": "Trainee", "estágio": "Estágio",
    }
    for level in ordered:
        if any(variant.lower() in padded for variant in LEVEL_EXPANSIONS[level]):
            return canonical[level]
    return None

# Words that, when found in a job TITLE (with word-boundary context), indicate a senior position.
# Used to auto-exclude jobs when only júnior/pleno/estágio/trainee levels are selected.
# Checked as substrings of " {title_lower} " (with leading/trailing space for boundary).
SENIOR_TITLE_WORDS = [
    "senior", "sênior", " sr ", "sr.", "staff",
    " lead",         # matches "Team Lead", "DevOps Lead", "Engineering Lead", etc.
    "tech lead", "techlead", "lead developer", "lead engineer",
    "principal", "specialist", "especialista",
    "manager", "gerente", "head of", "head de", " head ",
    "architect", "arquiteto", "coordinator", "coordenador",
    "director", "diretor", " vp ", "c-level",
    "cto", "cio", "ciso", "engineering manager",
]

# Role incompatibility matrix: when searching for the key role, reject job titles
# that contain any of the listed terms. Prevents false positives (e.g. Full Stack → DevOps).
ROLE_INCOMPATIBILITY: dict[str, list[str]] = {
    "devops": [
        "full stack", "full-stack", "fullstack", "frontend", "front-end",
        "mobile developer", "ios developer", "android developer",
        "ui/ux designer", "product designer", "data scientist", "ml engineer",
    ],
    "devsecops": [
        "full stack", "full-stack", "fullstack", "frontend", "front-end", "mobile",
    ],
    "cloud engineer": [
        "full stack", "full-stack", "fullstack", "frontend", "front-end", "mobile",
    ],
    "platform engineer": [
        "full stack", "full-stack", "fullstack", "frontend", "front-end", "mobile",
    ],
    "sre": [
        "full stack", "full-stack", "fullstack", "frontend", "front-end", "mobile",
    ],
    "site reliability engineer": [
        "full stack", "full-stack", "fullstack", "frontend", "front-end", "mobile",
    ],
    "analista de infraestrutura": [
        "full stack", "full-stack", "fullstack", "frontend", "front-end", "mobile",
    ],
    "frontend": [
        "devops engineer", "platform engineer", "site reliability",
        "cloud engineer", " sre ", "infrastructure engineer",
    ],
    "backend": [
        "frontend developer", "front-end developer", "mobile developer",
        "ios developer", "android developer",
    ],
    "backend python": [
        "frontend developer", "front-end developer", "mobile developer",
    ],
    "backend .net": [
        "frontend developer", "front-end developer", "mobile developer",
    ],
}

# US-specific location markers: used to reject international jobs when accept_international=False.
US_LOCATION_MARKERS = [
    "united states", "remote, us", "remote - us", "remote (us)", "remote us only",
    "us remote", ", us ", "(us only)", "usa only",
    ", ca,", ", ny,", ", tx,", ", wa,", ", ma,", ", ga,", ", il,", ", co,",
    "san francisco", "new york city", "new york, ny", "seattle, wa",
    "austin, tx", "chicago, il", "los angeles", "boston, ma", "denver, co",
    "atlanta, ga",
]

DEFAULT_EXCLUDE_WORDS = [
    "Senior", "Sênior", "Sr", "Sr.", "Staff", "Lead", "Principal",
    "Manager", "Gerente", "Especialista", "Head", "Director", "Diretor",
    "VP", "C-Level", "CTO", "CIO", "CISO",
]


def expand_roles(role: str) -> list[str]:
    key = role.strip().lower()
    return ROLE_EXPANSIONS.get(key, [role])


def expand_roles_multi(roles: list[str]) -> list[str]:
    """Expand all roles and return a deduplicated list of role variants."""
    seen: set[str] = set()
    result: list[str] = []
    for role in roles:
        for variant in expand_roles(role):
            if variant not in seen:
                seen.add(variant)
                result.append(variant)
    return result


def expand_levels(level: str) -> list[str]:
    key = level.strip().lower()
    return LEVEL_EXPANSIONS.get(key, [level])
