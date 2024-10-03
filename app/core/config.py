from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Knowledge Intelligience"
    DEBUG: bool = False
    VERSION: str = "0.1.0"
    GOOGLE_API_KEY : str = "Dummy API Key"
    CHROME_DB_URI: str = "http://localhost:8000"
    UNSTRUCTURED_API_KEY: str = "Your Unstructured API Key"
    UNSTRUCTURED_API_URL: str = "http://localhost:12012"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    COHERE_API_KEY: str = "Your Cohere API Key"

    class Config:
        env_file = ".env"

settings = Settings()