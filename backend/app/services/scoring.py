"""
Isolated, testable match scoring and mandatory filter logic. No external I/O.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, TYPE_CHECKING

from app.core.expansions import SENIOR_TITLE_WORDS, ROLE_INCOMPATIBILITY, US_LOCATION_MARKERS

if TYPE_CHECKING:
    from app.schemas.search import SearchFilters
    from app.schemas.job import JobCreate


class MatchResult:
    def __init__(
        self,
        score: float,
        techs_found: list[str],
        techs_missing: list[str],
        positives: list[str],
        penalties: list[str],
        summary: str,
    ):
        self.score = round(min(max(score, 0), 100), 1)
        self.techs_found = techs_found
        self.techs_missing = techs_missing
        self.positives = positives
        self.penalties = penalties
        self.summary = summary


def _text_contains(text: str, term: str) -> bool:
    return term.lower() in text.lower()


def _any_in_text(text: str, terms: list[str]) -> list[str]:
    return [t for t in terms if _text_contains(text, t)]


def _is_us_only(location: Optional[str]) -> bool:
    if not location:
        return False
    loc = location.lower()
    return any(marker in loc for marker in US_LOCATION_MARKERS)


def _is_remote_job(title: str, location: Optional[str], modality: Optional[str]) -> bool:
    combined = f"{title} {location or ''}".lower()
    return (
        modality == "remote"
        or "remoto" in combined
        or "remote" in combined
        or "híbrido" in combined
        or "hybrid" in combined
    )


# Levels that are considered "non-senior" for auto-exclusion logic.
_JUNIOR_POOL = {"estágio", "trainee", "júnior", "pleno"}


def mandatory_reject(job: "JobCreate", filters: "SearchFilters") -> tuple[bool, str]:
    """
    Returns (True, reason) if this job must be rejected regardless of score.
    Returns (False, '') if the job passes all mandatory filters.

    Mandatory means: if violated, the job never appears — even at score 100.
    Called after deduplication, before scoring.
    """
    title = job.title or ""
    description = job.description or ""
    location = job.location
    modality = job.modality
    published_at = job.published_at
    level = job.level

    title_lower = title.lower()
    title_padded = f" {title_lower} "  # padding for word-boundary checks
    searchable = f"{title} {description}".lower()
    is_remote = _is_remote_job(title, location, modality)

    # 1. Excluded words in title (hard reject — they may appear in description for soft penalty)
    for word in filters.excluded_words:
        if word.lower() in title_lower:
            return True, f"Palavra excluída no título: '{word}'"

    # 2. All required words must appear somewhere in title+description
    if filters.required_words:
        missing = [w for w in filters.required_words if w.lower() not in searchable]
        if missing:
            return True, f"Palavras obrigatórias ausentes: {', '.join(missing)}"

    # Skills remain preferences unless the user explicitly requires a minimum.
    if filters.min_skill_matches > 0 and filters.technologies:
        matches = [skill for skill in filters.technologies if skill.lower() in searchable]
        required_count = min(filters.min_skill_matches, len(filters.technologies))
        if len(matches) < required_count:
            return True, f"Somente {len(matches)} de {required_count} habilidade(s) mínima(s) encontrada(s)"

    # 3. Senior title auto-exclusion: when only non-senior levels are selected,
    #    reject any job whose TITLE indicates a senior position.
    #    Note: we only look at title, not description — a mention of "Tech Lead" in
    #    the description context ("reporting to Tech Lead") must not reject the job.
    if filters.levels and all(lv.lower() in _JUNIOR_POOL for lv in filters.levels):
        for word in SENIOR_TITLE_WORDS:
            if word in title_padded:
                return True, f"Título indica nível sênior: '{word.strip()}'"

    # 4. Role incompatibility: prevent false positives like Full Stack in DevOps searches
    # Check incompatibility for ALL selected roles — reject only if incompatible with ALL of them
    roles_list = filters.roles if filters.roles else ([filters.role] if filters.role else [])
    if roles_list:
        all_incompatible_terms: list[str] = []
        for role_name in roles_list:
            role_key = role_name.strip().lower()
            all_incompatible_terms.extend(ROLE_INCOMPATIBILITY.get(role_key, []))
        # Deduplicate and check
        seen_terms: set[str] = set()
        for term in all_incompatible_terms:
            if term in seen_terms:
                continue
            seen_terms.add(term)
            # Only reject if this term is incompatible with ALL selected roles
            compatible_with_any = any(
                term not in ROLE_INCOMPATIBILITY.get(r.strip().lower(), [])
                for r in roles_list
            )
            if not compatible_with_any and term in title_lower:
                return True, f"Cargo incompatível: '{term}'"

    # 5. Date filter: use published_at (never collected_at)
    if filters.days_ago is not None and published_at is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=filters.days_ago)
        pub = published_at if published_at.tzinfo else published_at.replace(tzinfo=timezone.utc)
        if pub < cutoff:
            return True, f"Vaga mais antiga que {filters.days_ago} dia(s)"

    # 6. Level filter: reject known-level jobs that don't match selected levels.
    #    Jobs with level=None are kept unless include_unlevel=False (handled below).
    if filters.levels and level is not None:
        accepted = {lv.lower() for lv in filters.levels}
        if level.lower() not in accepted:
            return True, f"Nível '{level}' não está nos filtros selecionados"

    # 7. Jobs with unknown level: reject if include_unlevel is False and levels are selected.
    if filters.levels and not filters.include_unlevel and level is None:
        return True, "Nível não detectado e 'incluir sem nível' está desativado"

    # 8. Location filter: reject US-only jobs when accept_international=False.
    # Checked even for remote jobs: "Remote - US" markers indicate US-only remote roles.
    # Generic "Remote" location is not in US_LOCATION_MARKERS so it passes freely.
    if not filters.accept_international:
        if _is_us_only(location):
            return True, f"Vaga localizada nos EUA: '{location}'"

    # 9. Specific location match when mode is estado/cidade
    if filters.location_mode in ("estado", "cidade") and filters.location:
        loc_lower = (location or "").lower()
        if not is_remote and filters.location.lower() not in loc_lower:
            return True, f"Localização '{location}' não corresponde a '{filters.location}'"

    return False, ""


def calculate_match_score(
    title: str,
    description: str,
    company: str,
    location: Optional[str],
    modality: Optional[str],
    published_at: Optional[datetime],
    role_variants: list[str],
    level_variants: list[str],
    technologies: list[str],
    location_filter: Optional[str],
    remote_filter: bool,
    location_mode: str = "brasil",
    required_words: list[str] = [],
    excluded_words: list[str] = [],
) -> MatchResult:
    searchable = f"{title} {description or ''} {company}".lower()
    positives: list[str] = []
    penalties: list[str] = []
    score = 0.0
    techs_found: list[str] = []
    techs_missing: list[str] = []

    # --- Role: up to 30 pts ---
    role_hits = _any_in_text(searchable, role_variants)
    if role_hits:
        score += 30
        positives.append(f"Cargo compatível: {role_hits[0]}")

    # --- Technologies: up to 30 pts ---
    if technologies:
        techs_found = _any_in_text(searchable, technologies)
        techs_missing = [t for t in technologies if t not in techs_found]
        ratio = len(techs_found) / len(technologies)
        tech_pts = round(ratio * 30, 1)
        score += tech_pts
        if techs_found:
            positives.append(f"Tecnologias: {', '.join(techs_found)} ({len(techs_found)}/{len(technologies)})")

    # --- Level: up to 15 pts ---
    if level_variants:
        level_hits = _any_in_text(searchable, level_variants)
        if level_hits:
            score += 15
            positives.append(f"Nível: {level_hits[0]}")

    # --- Location + remote: up to 10 pts ---
    is_remote = _is_remote_job(title, location, modality)

    if remote_filter and is_remote:
        score += 10
        positives.append("Remoto")
    elif location_filter and location_filter.lower() in (location or "").lower():
        score += 7
        positives.append(f"Localização: {location}")
    elif not remote_filter and not location_filter:
        score += 5  # neutral

    # --- Recency: up to 10 pts ---
    if published_at:
        now = datetime.now(timezone.utc)
        pub = published_at if published_at.tzinfo else published_at.replace(tzinfo=timezone.utc)
        days_old = (now - pub).days
        if days_old <= 1:
            pts = 10
        elif days_old <= 3:
            pts = 8
        elif days_old <= 7:
            pts = 6
        elif days_old <= 15:
            pts = 3
        else:
            pts = 1
        score += pts
        positives.append(f"Publicada há {days_old} dia(s)")

    # --- Required words: up to 5 pts ---
    if required_words:
        req_hits = _any_in_text(searchable, required_words)
        ratio = len(req_hits) / len(required_words)
        score += round(ratio * 5, 1)
        if req_hits:
            positives.append(f"Palavras obrigatórias: {', '.join(req_hits)}")

    # --- Excluded words in description: soft penalty -30 each ---
    # (hard reject on title is done in mandatory_reject; this handles description mentions)
    excl_hits = _any_in_text(searchable, excluded_words)
    for word in excl_hits:
        score -= 30
        penalties.append(f"Palavra excluída na descrição: '{word}'")

    summary_parts = []
    if positives:
        summary_parts.append("; ".join(positives[:3]))
    if penalties:
        summary_parts.append("; ".join(penalties))

    summary = " | ".join(summary_parts) if summary_parts else "Sem correspondências"

    return MatchResult(
        score=score,
        techs_found=techs_found,
        techs_missing=techs_missing,
        positives=positives,
        penalties=penalties,
        summary=summary,
    )
