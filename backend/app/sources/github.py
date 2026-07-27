"""
GitHub public repos with job listings (vagas).
Uses GitHub Search API (unauthenticated: 10 req/min).

NOTE: issues in community repos are often weeks old — days_ago filter is not applied
here since an old issue is still an open job. Recency is handled by the scorer.
"""
import logging
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.expansions import expand_roles_multi, expand_levels
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource
from app.utils.url_validator import is_safe_url

logger = logging.getLogger(__name__)

# Repos confirmed to exist with open issues.
# Mapped to relevant roles so we don't search backend repos for DevOps jobs.
GITHUB_REPOS = [
    {
        "owner": "backend-br", "repo": "vagas", "label": "Backend BR",
        "roles": ["backend", "python", ".net", "java", "go", "node", "full stack", "full-stack"],
    },
    {
        "owner": "frontendbr", "repo": "vagas", "label": "Frontend BR",
        "roles": ["frontend", "front-end", "react", "vue", "angular", "full stack", "full-stack"],
    },
    # devops-br/vagas does NOT exist — do not add
]

# Per-category GitHub-friendly search terms
ROLE_GITHUB_TERMS: dict[str, list[str]] = {
    "devops":    ["DevOps", "Platform Engineer", "SRE", "Infrastructure Engineer", "DevSecOps", "Cloud Engineer"],
    "cloud":     ["Cloud Engineer", "Cloud Infrastructure", "Platform Engineer", "SRE"],
    "sre":       ["SRE", "Site Reliability", "Platform Engineer", "DevOps"],
    "platform":  ["Platform Engineer", "Infrastructure Engineer", "SRE", "DevOps"],
    "security":  ["Security Engineer", "AppSec", "Pentest", "InfoSec", "SOC", "DevSecOps"],
    "backend":   ["Backend", "Python Developer", "Node.js", "Java Developer", "Golang", ".NET"],
    "frontend":  ["Frontend", "React", "Vue", "Angular", "TypeScript", "JavaScript"],
    "full stack":["Full Stack", "Full-Stack", "Backend", "Frontend"],
}

SEARCH_URL = "https://api.github.com/search/issues"


def _role_to_github_terms(role: str, role_terms: list[str]) -> list[str]:
    role_lower = role.lower()
    for key, terms in ROLE_GITHUB_TERMS.items():
        if key in role_lower:
            return terms
    return role_terms[:5]


def _repo_matches_role(repo_roles: list[str], role: str) -> bool:
    """Return True if this repo is relevant for the given role."""
    role_lower = role.lower()
    return any(r in role_lower for r in repo_roles)


class GitHubSource(BaseSource):
    name = "github"

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        roles_list = filters.roles if filters.roles else ([filters.role] if filters.role else [])
        role_terms = expand_roles_multi(roles_list)
        if not role_terms:
            role_terms = roles_list

        # Use primary role for GitHub category matching
        primary_role = roles_list[0] if roles_list else ""
        github_terms = _role_to_github_terms(primary_role, role_terms)
        query_role = " OR ".join(f'"{t}"' for t in github_terms[:5])

        results: list[JobCreate] = []
        collected_at = datetime.now(timezone.utc)

        async with httpx.AsyncClient(
            timeout=settings.request_timeout,
            headers={
                "User-Agent": settings.user_agent,
                "Accept": "application/vnd.github.v3+json",
            },
        ) as client:
            for repo_info in GITHUB_REPOS:
                # Skip repos that don't match any of the searched roles
                if not any(_repo_matches_role(repo_info["roles"], r) for r in roles_list):
                    continue

                repo = f"{repo_info['owner']}/{repo_info['repo']}"
                # in:title restricts match to issue title only, avoiding false positives
                q = f"{query_role} repo:{repo} is:issue is:open in:title"

                try:
                    resp = await client.get(
                        SEARCH_URL,
                        params={"q": q, "per_page": 30, "sort": "created", "order": "desc"},
                    )
                    if resp.status_code == 403:
                        logger.warning("GitHub rate limit reached")
                        break
                    if resp.status_code == 422:
                        logger.debug("GitHub search 422 for repo %s (may not exist)", repo)
                        continue
                    if resp.status_code != 200:
                        logger.debug("GitHub search HTTP %s for %s", resp.status_code, repo)
                        continue
                    data = resp.json()
                except Exception as e:
                    logger.debug("GitHub %s error: %s", repo, e)
                    continue

                for issue in data.get("items", []):
                    title = issue.get("title", "")
                    url = issue.get("html_url", "")

                    if not url or not is_safe_url(url):
                        continue

                    created_raw = issue.get("created_at")
                    pub = None
                    if created_raw:
                        try:
                            pub = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                        except Exception:
                            pass

                    body = issue.get("body", "") or ""
                    searchable = f"{title} {body}".lower()
                    techs = [t for t in filters.technologies if t.lower() in searchable]

                    modality = "remote" if ("remoto" in searchable or "remote" in searchable) else None
                    if filters.remote and modality != "remote":
                        continue

                    # label detection
                    labels = [la.get("name", "") for la in (issue.get("labels") or [])]
                    level = None
                    for la in labels:
                        la_lower = la.lower()
                        if any(w in la_lower for w in ["estágio", "estagio", "intern"]):
                            level = "Estágio"
                        elif any(w in la_lower for w in ["júnior", "junior", "jr"]):
                            level = "Júnior"
                        elif any(w in la_lower for w in ["pleno", "mid"]):
                            level = "Pleno"

                    results.append(
                        JobCreate(
                            title=title,
                            company=repo_info["label"],
                            location=None,
                            modality=modality,
                            level=level,
                            description=body[:400] or None,
                            technologies=techs,
                            source=self.name,
                            url=url,
                            apply_url=url,
                            published_at=pub,
                            collected_at=collected_at,
                            is_manual=False,
                            external_id=str(issue.get("id", "")),
                        )
                    )

        return results[: filters.max_results]
