from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Knowledge Intelligence"
    DEBUG: bool = False
    VERSION: str = "0.1.0"
    GOOGLE_API_KEY: str = "Dummy API Key"
    CHROME_DB_URI: str = "http://localhost:8000"
    UNSTRUCTURED_API_KEY: str = "Your Unstructured API Key"
    UNSTRUCTURED_API_URL: str = "http://localhost:12012"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    COHERE_API_KEY: str = "Your Cohere API Key"

    class Config:
        env_file = ".env"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adjust settings for Docker environment
        if self.REDIS_HOST == "redis":
            self.CHROME_DB_URI = "http://chroma:8000"
            self.UNSTRUCTURED_API_URL = "http://unstructured-api:8000"

settings = Settings()