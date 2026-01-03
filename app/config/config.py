from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: AnyUrl  # Validates that the URL is properly formatted
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GROQ_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url_str(self) -> str:
        return str(self.DATABASE_URL)

settings = Settings()