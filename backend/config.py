from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Fallback to localhost if no .env is found; overridden by .env file
    ollama_host: str = "http://192.168.137.212:11434"
    default_model: str = "phi3.5"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()