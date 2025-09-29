from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LUSHA_API_KEY: str
    LUSHA_API_SECRET: str
    LUSHA_CSRF_TOKEN: str
    LUSHA_XSRF_TOKEN: str
    LUSHA_COOKIE: str

    class Config:
        env_file = ".env.dev"


settings = Settings()
