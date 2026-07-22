"""
MotoMod AI — Core Configuration
Pydantic Settings v2 with full environment variable support
"""
from functools import lru_cache
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────────────
    APP_NAME: str = "MotoMod AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-generate-with-openssl-rand-hex-32"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # ─── API ─────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"

    @field_validator("DOCS_URL", "REDOC_URL", mode="before")
    @classmethod
    def hide_docs_in_production(cls, v: Optional[str], info) -> Optional[str]:
        # Docs hidden in production by default; can override
        return v

    # ─── JWT ─────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-generate-with-openssl-rand-hex-64"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ─── PostgreSQL ───────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "motomod_ai"
    POSTGRES_USER: str = "motomod"
    POSTGRES_PASSWORD: str = "motomod_dev_password"
    DATABASE_URL: str = "postgresql+asyncpg://motomod:motomod_dev_password@localhost:5432/motomod_ai"
    DATABASE_SYNC_URL: str = "postgresql+psycopg2://motomod:motomod_dev_password@localhost:5432/motomod_ai"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30

    # ─── Redis ───────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300
    CACHE_TTL_BIKE_SECONDS: int = 3600
    CACHE_TTL_PREDICTION_SECONDS: int = 1800

    # ─── MinIO ───────────────────────────────────────────────
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "motomod_admin"
    MINIO_SECRET_KEY: str = "motomod_secret"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_BIKES: str = "motomod-bikes"
    MINIO_BUCKET_MODS: str = "motomod-modifications"
    MINIO_BUCKET_USERS: str = "motomod-users"
    MINIO_BUCKET_BUILDS: str = "motomod-builds"
    MINIO_BUCKET_ML: str = "motomod-ml-models"
    MINIO_BUCKET_DATASETS: str = "motomod-datasets"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_DATASET_TYPES: List[str] = ["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/json"]

    # ─── Celery ──────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_TIMEZONE: str = "Asia/Kolkata"
    CELERY_WORKER_CONCURRENCY: int = 4

    # ─── MLflow ──────────────────────────────────────────────
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "motomod_ai"
    ML_MODELS_DIR: str = "./ml/models/trained"
    ML_INFERENCE_BATCH_SIZE: int = 32
    ML_CONFIDENCE_THRESHOLD: float = 0.7

    # ─── Razorpay ────────────────────────────────────────────
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    RAZORPAY_CURRENCY: str = "INR"

    # ─── Email ────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@motomod.ai"
    SMTP_FROM_NAME: str = "MotoMod AI"

    # ─── Rate Limiting ───────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_AI_PER_MINUTE: int = 20

    # ─── Logging ─────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: Optional[str] = None

    # ─── Monitoring ──────────────────────────────────────────
    PROMETHEUS_ENABLED: bool = True

    # ─── ETL ─────────────────────────────────────────────────
    ETL_SCHEDULE_CRON: str = "0 2 * * *"
    ETL_MAX_FILE_SIZE_MB: int = 500

    # ─── Admin ───────────────────────────────────────────────
    ADMIN_EMAIL: str = "admin@motomod.ai"
    ADMIN_PASSWORD: str = "Admin@MotoMod2024!"
    ADMIN_NAME: str = "MotoMod Admin"

    # ─── Computed Properties ─────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def effective_docs_url(self) -> Optional[str]:
        return None if self.is_production else self.DOCS_URL

    @property
    def effective_redoc_url(self) -> Optional[str]:
        return None if self.is_production else self.REDOC_URL


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
