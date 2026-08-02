from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    agent_mode: str = "mock"
    tavily_api_key: str = ""
    enabled_tools: str = (
        "web_search,page_reader,draft_email,send_email,create_ticket,schedule_meeting"
    )
    api_cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def tools(self) -> set[str]:
        return {v.strip() for v in self.enabled_tools.split(",") if v.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
