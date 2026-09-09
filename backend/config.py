from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Fallback to LAN host IP if no .env is found; overridden by .env file
    ollama_host: str = "http://127.0.0.1:11434"
    default_model: str = "phi3.5:latest"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
