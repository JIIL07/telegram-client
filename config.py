from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_id: int
    api_hash: str
    session_name: str = "session"

    postgres_dsn: str

    myaso_api_url: str
    myaso_forward_endpoint: str = "/get_message"
    myaso_api_timeout_seconds: float = 20.0

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def myaso_forward_url(self) -> str:
        base = self.myaso_api_url.rstrip("/")
        endpoint = self.myaso_forward_endpoint
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"{base}{endpoint}"


settings = Settings()
