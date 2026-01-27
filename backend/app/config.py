from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'Resumetry API'
    debug: bool = False
    cors_origins: list[str] = ['http://localhost:4200', 'http://localhost:3000']

    # DynamoDB settings
    dynamodb_endpoint: Optional[str] = None  # None = use real AWS, set for local
    dynamodb_region: str = 'us-east-1'
    dynamodb_table: str = 'resumetry-job-applications'

    class Config:
        env_prefix = 'RESUMETRY_'


settings = Settings()
