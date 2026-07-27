from abc import ABC, abstractmethod
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters


class BaseSource(ABC):
    name: str = "base"
    is_manual: bool = False

    @abstractmethod
    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        """Execute search and return normalized jobs. Must not raise."""
        ...
