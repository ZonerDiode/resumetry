from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'ResumeTry API'
    debug: bool = False
    cors_origins: list[str] = ['http://localhost:4200', 'http://localhost:3000']

    class Config:
        env_prefix = 'RESUMETRY_'


settings = Settings()
