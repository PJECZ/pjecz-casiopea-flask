"""
Settings
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource


class Settings(BaseSettings):
    """Settings"""

    # Variables de entorno
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    FERNET_KEY: str = os.getenv("FERNET_KEY", "")
    HOST: str = os.getenv("HOST", "")
    PREFIX: str = os.getenv("PREFIX", "")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")
    SALT: str = os.getenv("SALT", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "")
    TASK_QUEUE_NAME: str = os.getenv("TASK_QUEUE_NAME", "pjecz_casiopea")
    TZ: str = os.getenv("TZ", "America/Mexico_City")
    NEW_ACCOUNT_CONFIRM_URL: str = os.getenv("NEW_ACCOUNT_CONFIRM_URL", "")
    RECOVER_ACCOUNT_CONFIRM_URL: str = os.getenv("RECOVER_ACCOUNT_CONFIRM_URL", "")
    TURNOS_API_KEY: str = os.getenv("TURNOS_API_KEY", "")
    TURNOS_API_KEY_URL: str = os.getenv("TURNOS_API_KEY_URL", "")
    TURNOS_USUARIO_ID: int = os.getenv("TURNOS_USUARIO_ID", 0)
    TURNOS_TIPO_ID: int = os.getenv("TURNOS_TIPO_ID", 0)
    TWO_FACTOR_AUTHENTICATION_ENABLED: bool = os.getenv("TWO_FACTOR_AUTHENTICATION_ENABLED", "False").lower() in ("true", "1", "t")
    # Variables de Banneo
    BAN_MAX_ATTEMPTS: int = os.getenv("BAN_MAX_ATTEMPTS", 5)
    BAN_DURATION_MINUTES: int = os.getenv("BAN_DURATION_MINUTES", 30)
    BAN_MAX_ATTEMPTS_PER_DAY: int = os.getenv("BAN_MAX_ATTEMPTS_PER_DAY", 3)
    # Número de proxies de confianza delante de la app, 0 si no hay; con Cloud Run es 1
    PROXY_FIX_X_FOR: int = os.getenv("PROXY_FIX_X_FOR", 0)

    # Incrementar el tamaño de lo que se sube en los formularios
    MAX_CONTENT_LENGTH: int | None = None
    MAX_FORM_MEMORY_SIZE: int = 50 * (2**10) ** 2  # 50 MB

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Change the order of precedence of settings sources"""
        return env_settings, file_secret_settings, init_settings


@lru_cache()
def get_settings() -> Settings:
    """Get Settings"""
    return Settings()
