"""
Generates manual search links for LinkedIn, Google, etc.
Returns job cards with is_manual=True and a pre-built search URL.
No HTTP requests made.
"""
import urllib.parse
from datetime import datetime, timezone

from app.core.expansions import expand_roles_multi, expand_levels
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource


DAYS_MAP = {7: "r604800", 14: "r1209600", 30: "r2592000"}


def _build_linkedin_url(role_terms: list[str], filters: SearchFilters) -> str:
    keywords = " OR ".join(f'"{t}"' for t in role_terms[:3])
    params: dict = {"keywords": keywords, "f_TPR": "", "f_WT": ""}

    if filters.remote:
        params["f_WT"] = "2"  # remote
    if filters.days_ago:
        params["f_TPR"] = DAYS_MAP.get(filters.days_ago, "")
    if filters.location and filters.location_mode not in ("internacional", "brasil_internacional"):
        params["location"] = filters.location

    return "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(
        {k: v for k, v in params.items() if v}, quote_via=urllib.parse.quote
    )


def _build_google_linkedin_url(role_terms: list[str], level_terms: list[str], filters: SearchFilters) -> str:
    role_part = " OR ".join(f'"{t}"' for t in role_terms[:3])
    level_part = (" OR ".join(f'"{t}"' for t in level_terms[:3])) if level_terms else ""
    tech_part = " OR ".join(f'"{t}"' for t in filters.technologies[:4]) if filters.technologies else ""

    query = f'site:linkedin.com/jobs/view ({role_part})'
    if level_part:
        query += f' ({level_part})'
    if tech_part:
        query += f' ({tech_part})'
    if filters.location and filters.location_mode not in ("internacional", "brasil_internacional"):
        query += f' {filters.location}'

    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


def _build_google_posts_url(role_terms: list[str]) -> str:
    role_part = " OR ".join(f'"{t}"' for t in role_terms[:3])
    query = f'site:linkedin.com/posts ("estamos contratando" OR "vaga aberta" OR hiring) ({role_part})'
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


def _build_google_recruiters_url(role_terms: list[str]) -> str:
    role_part = " OR ".join(f'"{t}"' for t in role_terms[:3])
    query = f'site:linkedin.com/in ("Tech Recruiter" OR "Talent Acquisition") ({role_part}) Brasil'
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


def _build_google_gupy_url(role_terms: list[str], level_terms: list[str]) -> str:
    role_part = " OR ".join(f'"{t}"' for t in role_terms[:3])
    level_part = (" OR ".join(f'"{t}"' for t in level_terms[:3])) if level_terms else ""
    query = f'site:gupy.io ({role_part})'
    if level_part:
        query += f' ({level_part})'
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


def _build_gupy_portal_url(role: str) -> str:
    return "https://portal.gupy.io/?searchTerm=" + urllib.parse.quote(role)


def _build_google_lever_url(role_terms: list[str], level_terms: list[str]) -> str:
    role_part = " OR ".join(f'"{t}"' for t in role_terms[:4])
    level_part = (" OR ".join(f'"{t}"' for t in level_terms[:3])) if level_terms else ""
    query = f'site:jobs.lever.co ({role_part})'
    if level_part:
        query += f' ({level_part})'
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


def _build_infojobs_url(role: str) -> str:
    return "https://www.infojobs.com.br/empregos.aspx?q=" + urllib.parse.quote(role)


def _build_vagas_com_url(role: str) -> str:
    return "https://www.vagas.com.br/vagas-de-" + urllib.parse.quote(role.lower().replace(" ", "-"))


class ManualSearchSource(BaseSource):
    name = "manual_search"
    is_manual = True

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        roles_list = filters.roles if filters.roles else ([filters.role] if filters.role else [])
        role_terms = expand_roles_multi(roles_list)
        if not role_terms:
            role_terms = roles_list
        primary_role = roles_list[0] if roles_list else (filters.role or "")

        level_terms: list[str] = []
        for lvl in filters.levels:
            level_terms.extend(expand_levels(lvl))

        now = datetime.now(timezone.utc)

        searches = [
            {
                "title": f"LinkedIn Jobs — {primary_role}",
                "company": "LinkedIn",
                "url": _build_linkedin_url(role_terms, filters),
                "description": "Pesquisa direta no LinkedIn Jobs com os filtros aplicados.",
            },
            {
                "title": f"Gupy Portal — {primary_role}",
                "company": "Gupy",
                "url": _build_gupy_portal_url(primary_role),
                "description": "Pesquisa no portal centralizado do Gupy.",
            },
            {
                "title": f"Vagas.com.br — {primary_role}",
                "company": "Vagas.com.br",
                "url": _build_vagas_com_url(primary_role),
                "description": "Pesquisa no Vagas.com.br.",
            },
            {
                "title": f"InfoJobs — {primary_role}",
                "company": "InfoJobs",
                "url": _build_infojobs_url(primary_role),
                "description": "Pesquisa no InfoJobs Brasil.",
            },
            {
                "title": f"Google → LinkedIn vagas: {primary_role}",
                "company": "Google / LinkedIn",
                "url": _build_google_linkedin_url(role_terms, level_terms, filters),
                "description": "Busca Google por vagas no LinkedIn com cargo e nível.",
            },
            {
                "title": f"Google → Lever: {primary_role}",
                "company": "Google / Lever",
                "url": _build_google_lever_url(role_terms, level_terms),
                "description": "Vagas em empresas que usam Lever, buscadas via Google.",
            },
            {
                "title": f"Google → Gupy: {primary_role}",
                "company": "Google / Gupy",
                "url": _build_google_gupy_url(role_terms, level_terms),
                "description": "Vagas no Gupy via Google.",
            },
            {
                "title": f"Google → posts de contratação: {primary_role}",
                "company": "Google / LinkedIn",
                "url": _build_google_posts_url(role_terms),
                "description": "Busca Google por posts de contratação no LinkedIn.",
            },
            {
                "title": f"Google → recrutadores: {primary_role}",
                "company": "Google / LinkedIn",
                "url": _build_google_recruiters_url(role_terms),
                "description": "Encontre recrutadores de tecnologia no LinkedIn.",
            },
        ]

        results: list[JobCreate] = []
        for s in searches:
            results.append(
                JobCreate(
                    title=s["title"],
                    company=s["company"],
                    location=filters.location,
                    modality="remote" if filters.remote else None,
                    level=", ".join(filters.levels) if filters.levels else None,
                    description=s["description"],
                    technologies=[],
                    source=self.name,
                    url=s["url"],
                    apply_url=s["url"],
                    published_at=None,
                    collected_at=now,
                    match_score=0.0,
                    is_manual=True,
                )
            )

        return results
