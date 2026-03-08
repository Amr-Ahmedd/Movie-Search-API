from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    omdb_api_key: str
    tmdb_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )


settings = Settings()