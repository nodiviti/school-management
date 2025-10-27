"""Application Configuration"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "School Management System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str
    API_PREFIX: str = "/api"
    
    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8001
    CORS_ORIGINS: str = "*"
    
    # Database
    DATABASE_TYPE: str = "postgresql"  # postgresql | mongodb
    POSTGRES_URL: Optional[str] = None
    MONGO_URL: Optional[str] = None
    DB_NAME: str = "school_management_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    
    # 2FA
    ENABLE_2FA: bool = True
    TOTP_ISSUER: str = "School Management System"
    
    # Object Storage
    STORAGE_PROVIDER: str = "minio"  # minio | s3 | gcs | azure
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "school-files"
    MINIO_USE_SSL: bool = False
    
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None
    
    GCS_PROJECT_ID: Optional[str] = None
    GCS_BUCKET_NAME: Optional[str] = None
    GCS_CREDENTIALS_FILE: Optional[str] = None
    
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_CONTAINER_NAME: Optional[str] = None
    
    MAX_FILE_SIZE_MB: int = 10
    
    # Email (SMTP)
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@school.com"
    SMTP_FROM_NAME: str = "School Management System"
    SMTP_USE_TLS: bool = False
    
    # Payment Gateway
    PAYMENT_GATEWAY: str = "midtrans"  # midtrans | xendit | stripe | bayarind
    MIDTRANS_SERVER_KEY: Optional[str] = None
    MIDTRANS_CLIENT_KEY: Optional[str] = None
    MIDTRANS_IS_PRODUCTION: bool = False
    
    XENDIT_SECRET_KEY: Optional[str] = None
    XENDIT_PUBLIC_KEY: Optional[str] = None
    
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLIC_KEY: Optional[str] = None
    
    BAYARIND_API_KEY: Optional[str] = None
    BAYARIND_MERCHANT_ID: Optional[str] = None
    
    PAYMENT_CURRENCY: str = "IDR"
    
    # LMS Integration
    LMS_ENABLED: bool = False
    LMS_PROVIDER: str = "moodle"
    MOODLE_URL: Optional[str] = None
    MOODLE_TOKEN: Optional[str] = None
    LMS_SYNC_MODE: str = "push"
    LMS_AUTO_SYNC_ENABLED: bool = False
    
    # LLM
    LLM_ENABLED: bool = False
    LLM_PROVIDER: str = "openai"
    EMERGENT_LLM_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENABLED: bool = False
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Features
    FEATURE_ADMISSIONS: bool = True
    FEATURE_DORMITORY: bool = True
    FEATURE_LIBRARY: bool = True
    FEATURE_ATTENDANCE_QR: bool = True
    
    # Audit
    AUDIT_LOG_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()