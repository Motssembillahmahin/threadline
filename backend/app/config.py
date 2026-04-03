from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    ACCESS_SECRET: str
    REFRESH_SECRET: str
    UPLOAD_DIR: str = "/app/static/uploads"
    CORS_ORIGINS: str = "http://localhost:3000"
    # "development" | "production"
    ENVIRONMENT: str = "development"
    # Set to enable Cloudinary uploads (leave empty to use local storage)
    CLOUDINARY_URL: str = ""

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
