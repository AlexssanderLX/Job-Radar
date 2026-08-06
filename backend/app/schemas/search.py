from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class SearchFilters(BaseModel):
    # Multi-role support — preferred
    roles: list[str] = []
    # Deprecated single-role alias — maps to roles[0] for backward compat
    role: Optional[str] = None

    levels: list[str] = []
    technologies: list[str] = []
    min_skill_matches: int = 0
    location: Optional[str] = None
    # Location mode controls how location + remote filtering is applied:
    # "brasil"        - jobs in Brazil (or remote-labeled)
    # "estado"        - jobs in a specific state (location field)
    # "cidade"        - jobs in a specific city (location field)
    # "remoto_brasil" - remote jobs (work from anywhere in Brazil)
    # "remoto_latam"  - remote jobs open to LATAM
    # "remoto_global" - any remote job worldwide
    # "internacional" - all jobs, including US-only positions
    location_mode: str = "brasil"
    remote: bool = False           # synced from location_mode by validator
    accept_international: bool = False  # synced from location_mode by validator
    include_unlevel: bool = True  # include jobs whose source does not expose a level
    days_ago: Optional[int] = None
    required_words: list[str] = []
    excluded_words: list[str] = []
    sources: list[str] = []
    max_results: int = 100
    strategy: str = "balanced"  # exact, balanced, broad

    @field_validator("max_results")
    @classmethod
    def cap_results(cls, v: int) -> int:
        return min(v, 500)

    @field_validator("min_skill_matches")
    @classmethod
    def valid_min_skill_matches(cls, v: int) -> int:
        return max(0, min(v, 50))

    @field_validator("location")
    @classmethod
    def empty_to_none(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            return None
        return v

    @model_validator(mode="after")
    def sync_roles_and_location(self) -> "SearchFilters":
        # Handle backward compat: role (str) → roles (list)
        if self.role and not self.roles:
            self.roles = [self.role]
        elif self.roles and not self.role:
            self.role = self.roles[0]
        elif not self.roles and not self.role:
            self.roles = []
            self.role = ""

        mode = self.location_mode
        if mode in ("remoto_brasil", "remoto_latam"):
            self.remote = True
            self.accept_international = False
        elif mode == "remoto_global":
            self.remote = True
            self.accept_international = True
        elif mode == "internacional":
            self.remote = False
            self.accept_international = True
        else:
            self.remote = False
            self.accept_international = False
        if mode == "brasil" and self.location is None:
            self.location = "Brasil"
        return self


class SearchResult(BaseModel):
    search_id: int
    total_raw: int
    total_deduplicated: int
    sources_searched: list[str]
    sources_failed: list[str]
    duration_seconds: float
    jobs: list
    source_progress: list[dict] = []


class SavedFilterCreate(BaseModel):
    name: str
    filters: SearchFilters


class SavedFilterRead(BaseModel):
    id: int
    name: str
    filters: SearchFilters
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchHistoryRead(BaseModel):
    id: int
    filters: dict
    searched_at: datetime
    total_found: int
    sources_searched: list[str]
    sources_failed: list[str]
    duration_seconds: float

    class Config:
        from_attributes = True
