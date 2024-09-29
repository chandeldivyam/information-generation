from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Your RAG Microservice"
    DEBUG: bool = False
    VERSION: str = "0.1.0"

    class Config:
        env_file = ".env"

settings = Settings()