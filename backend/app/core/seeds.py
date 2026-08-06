"""
Seed default data (roles, skills, sources) if tables are empty.
This function is idempotent — safe to call on every startup.
"""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.role import Role
from app.models.skill import Skill
from app.models.source import Source

DEFAULT_ROLES = [
    {
        "name": "DevOps",
        "category": "infrastructure",
        "description": "DevOps Engineer — automação, CI/CD, infraestrutura",
        "aliases": [
            "DevOps", "DevOps Engineer", "Analista DevOps", "Cloud Engineer",
            "Platform Engineer", "Infrastructure Engineer", "SRE",
            "Site Reliability Engineer", "DevSecOps",
        ],
        "excluded_words": ["full stack", "fullstack", "frontend", "mobile"],
    },
    {
        "name": "DevSecOps",
        "category": "security",
        "description": "DevSecOps Engineer — segurança integrada ao pipeline",
        "aliases": [
            "DevSecOps", "DevSecOps Engineer", "Security Engineer DevOps",
            "Platform Security Engineer",
        ],
        "excluded_words": ["full stack", "fullstack", "frontend", "mobile"],
    },
    {
        "name": "Desenvolvedor Backend",
        "category": "development",
        "description": "Desenvolvedor Backend — API, serviços, banco de dados",
        "aliases": [
            "Backend Developer", "Desenvolvedor Backend", "Back-end Developer",
            "Software Engineer", "Software Developer",
        ],
        "excluded_words": ["frontend", "mobile", "ios", "android"],
    },
    {
        "name": "Backend Python",
        "category": "development",
        "description": "Desenvolvedor Backend com Python",
        "aliases": [
            "Python Developer", "Backend Python", "Python Engineer",
            "Software Engineer Python", "Desenvolvedor Python",
        ],
        "excluded_words": ["frontend", "mobile"],
    },
    {
        "name": "Backend .NET",
        "category": "development",
        "description": "Desenvolvedor Backend com .NET / C#",
        "aliases": [
            ".NET Developer", "Backend .NET", "C# Developer",
            "Software Engineer .NET", "Desenvolvedor .NET",
        ],
        "excluded_words": ["frontend", "mobile"],
    },
    {
        "name": "Cloud Engineer",
        "category": "infrastructure",
        "description": "Cloud Engineer — AWS, Azure, GCP",
        "aliases": [
            "Cloud Engineer", "Cloud Architect", "AWS Engineer",
            "Azure Engineer", "GCP Engineer", "Cloud Infrastructure",
        ],
        "excluded_words": ["full stack", "fullstack", "frontend", "mobile"],
    },
    {
        "name": "Platform Engineer",
        "category": "infrastructure",
        "description": "Platform Engineer — plataformas internas, IDP",
        "aliases": [
            "Platform Engineer", "Infrastructure Engineer", "DevOps",
            "SRE", "Cloud Platform Engineer",
        ],
        "excluded_words": ["full stack", "fullstack", "frontend", "mobile"],
    },
    {
        "name": "Site Reliability Engineer",
        "category": "infrastructure",
        "description": "SRE — confiabilidade, observabilidade, SLO/SLA",
        "aliases": [
            "SRE", "Site Reliability Engineer", "Platform Engineer",
            "DevOps Engineer", "Infrastructure Engineer",
        ],
        "excluded_words": ["full stack", "fullstack", "frontend", "mobile"],
    },
    {
        "name": "Application Security",
        "category": "security",
        "description": "Application Security / AppSec",
        "aliases": [
            "Application Security", "AppSec Engineer", "Security Engineer",
            "Penetration Tester", "SAST DAST", "Segurança de Aplicações",
        ],
        "excluded_words": [],
    },
    {
        "name": "Segurança da Informação",
        "category": "security",
        "description": "Analista de Segurança da Informação / InfoSec",
        "aliases": [
            "Segurança da Informação", "Information Security", "InfoSec",
            "Analista de Segurança", "Cybersecurity Analyst",
        ],
        "excluded_words": [],
    },
    {
        "name": "Analista de Infraestrutura",
        "category": "infrastructure",
        "description": "Analista de Infraestrutura / Sysadmin",
        "aliases": [
            "Analista de Infraestrutura", "Infrastructure Analyst",
            "Sysadmin", "Administrador de Sistemas",
        ],
        "excluded_words": ["full stack", "fullstack", "frontend", "mobile"],
    },
    {
        "name": "Suporte Cloud",
        "category": "infrastructure",
        "description": "Suporte Cloud / Cloud Operations",
        "aliases": [
            "Suporte Cloud", "Cloud Support", "Cloud Operations",
            "Analista de Suporte Cloud",
        ],
        "excluded_words": [],
    },
    {
        "name": "Desenvolvedor Full Stack",
        "category": "development",
        "description": "Desenvolvedor Full Stack — frontend + backend",
        "aliases": [
            "Full Stack Developer", "Desenvolvedor Full Stack",
            "Fullstack Engineer", "Full-Stack Developer",
        ],
        "excluded_words": [],
    },
]

DEFAULT_SKILLS = [
    {"name": "Python", "category": "language", "aliases": ["python", "Python3", "py"]},
    {"name": "C#", "category": "language", "aliases": ["csharp", "C Sharp", "dotnet-csharp"]},
    {"name": ".NET", "category": "framework", "aliases": ["dotnet", "dot net", ".NET Core", "ASP.NET"]},
    {"name": "Docker", "category": "devops", "aliases": ["docker", "Docker Container", "containerização"]},
    {"name": "Linux", "category": "os", "aliases": ["linux", "Ubuntu", "CentOS", "Debian", "bash", "shell"]},
    {"name": "GitHub Actions", "category": "cicd", "aliases": ["github actions", "GHA", "github-actions"]},
    {"name": "GitLab CI", "category": "cicd", "aliases": ["gitlab ci", "gitlab-ci", "gitlab ci/cd"]},
    {"name": "Azure", "category": "cloud", "aliases": ["azure", "Microsoft Azure", "Azure Cloud"]},
    {"name": "AWS", "category": "cloud", "aliases": ["aws", "Amazon Web Services", "Amazon AWS"]},
    {"name": "Google Cloud", "category": "cloud", "aliases": ["gcp", "google cloud", "GCP", "Google Cloud Platform"]},
    {"name": "Cloudflare", "category": "network", "aliases": ["cloudflare", "CF"]},
    {"name": "Nginx", "category": "infrastructure", "aliases": ["nginx", "NGINX", "nginx server"]},
    {"name": "CI/CD", "category": "cicd", "aliases": ["ci/cd", "CI CD", "continuous integration", "continuous delivery"]},
    {"name": "Terraform", "category": "iac", "aliases": ["terraform", "TF", "HCL"]},
    {"name": "Kubernetes", "category": "orchestration", "aliases": ["kubernetes", "k8s", "K8s", "Kubernetes Cluster"]},
    {"name": "PostgreSQL", "category": "database", "aliases": ["postgresql", "postgres", "pg", "Postgres"]},
    {"name": "MySQL", "category": "database", "aliases": ["mysql", "MariaDB"]},
    {"name": "FastAPI", "category": "framework", "aliases": ["fastapi", "Fast API"]},
    {"name": "React", "category": "frontend", "aliases": ["react", "ReactJS", "React.js"]},
    {"name": "Next.js", "category": "frontend", "aliases": ["nextjs", "next.js", "NextJS"]},
    {"name": "OWASP", "category": "security", "aliases": ["owasp", "OWASP Top 10"]},
    {"name": "Segurança", "category": "security", "aliases": ["segurança", "security", "cibersegurança", "cybersecurity"]},
]

DEFAULT_SOURCES = [
    {
        "name": "greenhouse",
        "display_name": "Greenhouse",
        "source_type": "connector",
        "is_manual": False,
        "priority": 1,
        "description": "API pública do Greenhouse Job Board — empresas tech",
    },
    {
        "name": "gupy",
        "display_name": "Gupy",
        "source_type": "connector",
        "is_manual": False,
        "priority": 2,
        "description": "API do Gupy — plataforma de recrutamento brasileira",
    },
    {
        "name": "github",
        "display_name": "GitHub Vagas",
        "source_type": "github",
        "is_manual": False,
        "priority": 3,
        "description": "Repositórios de vagas no GitHub (backend-br, frontendbr)",
    },
    {
        "name": "lever",
        "display_name": "Lever (via Google)",
        "source_type": "manual",
        "is_manual": True,
        "priority": 4,
        "description": "Links de busca Google para vagas em empresas que usam Lever",
    },
    {
        "name": "remotive",
        "display_name": "Remotive",
        "source_type": "connector",
        "is_manual": False,
        "priority": 4,
        "description": "Vagas remotas reais pela API pública da Remotive",
    },
    {
        "name": "remoteok",
        "display_name": "Remote OK",
        "source_type": "connector",
        "is_manual": False,
        "priority": 5,
        "description": "Vagas remotas reais pelo feed público da Remote OK",
    },
    {
        "name": "linkedin_jobs",
        "display_name": "LinkedIn Jobs",
        "source_type": "connector",
        "is_manual": False,
        "priority": 1,
        "description": "Vagas reais coletadas automaticamente da busca pública do LinkedIn",
    },
    {
        "name": "manual_search",
        "display_name": "Pesquisa Manual",
        "source_type": "manual",
        "is_manual": True,
        "priority": 5,
        "description": "Links de busca para LinkedIn, Gupy, Vagas.com e outros portais",
    },
]


async def seed_data(db: AsyncSession) -> None:
    """Insert default data if tables are empty. Safe to call multiple times."""
    now = datetime.utcnow()

    # Seed Roles
    result = await db.execute(select(Role).limit(1))
    if not result.scalars().first():
        for role_data in DEFAULT_ROLES:
            role = Role(
                name=role_data["name"],
                category=role_data.get("category"),
                description=role_data.get("description"),
                aliases=role_data.get("aliases", []),
                excluded_words=role_data.get("excluded_words", []),
                active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(role)

    # Seed Skills
    result = await db.execute(select(Skill).limit(1))
    if not result.scalars().first():
        for skill_data in DEFAULT_SKILLS:
            skill = Skill(
                name=skill_data["name"],
                category=skill_data.get("category"),
                aliases=skill_data.get("aliases", []),
                active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(skill)

    # Seed Sources
    result = await db.execute(select(Source).limit(1))
    if not result.scalars().first():
        for source_data in DEFAULT_SOURCES:
            source = Source(
                name=source_data["name"],
                display_name=source_data["display_name"],
                source_type=source_data["source_type"],
                is_manual=source_data.get("is_manual", False),
                priority=source_data.get("priority", 0),
                description=source_data.get("description"),
                active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(source)

    # Upgrade an older user-created LinkedIn link into the built-in automatic
    # connector while preserving its database identity and access history.
    linkedin_result = await db.execute(select(Source).where(Source.name == "linkedin_jobs"))
    linkedin_source = linkedin_result.scalars().first()
    if linkedin_source:
        linkedin_source.display_name = "LinkedIn Jobs"
        linkedin_source.source_type = "connector"
        linkedin_source.is_manual = False
        linkedin_source.active = True
        linkedin_source.description = "Vagas reais coletadas automaticamente da busca pública do LinkedIn"
        linkedin_source.updated_at = now
        db.add(linkedin_source)

    await db.commit()
