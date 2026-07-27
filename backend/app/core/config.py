from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Job Radar"
    database_url: str = "sqlite+aiosqlite:///./job_radar.db"
    request_timeout: float = 15.0
    max_concurrent_sources: int = 5
    cache_ttl_seconds: int = 300
    max_response_bytes: int = 5 * 1024 * 1024  # 5 MB
    user_agent: str = "JobRadar/1.0 (local job aggregator; educational use)"

    class Config:
        env_file = ".env"


settings = Settings()
