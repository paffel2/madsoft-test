from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
