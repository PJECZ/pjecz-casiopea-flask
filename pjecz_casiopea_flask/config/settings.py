"""
Settings
"""

import os
from functools import lru_cache

import google.auth
from dotenv import load_dotenv
from google.cloud import secretmanager
from pydantic_settings import BaseSettings

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID", "")  # Por defecto está vacío, esto significa estamos en modo local
SERVICE_PREFIX = os.getenv("SERVICE_PREFIX", "pjecz_casiopea_flask")
MEGABYTE = (2**10) ** 2


def get_secret(secret_id: str, default: str = "") -> str:
    """Get secret from Google Cloud Secret Manager"""

    # Si PROJECT_ID está vacío estamos en modo de desarrollo y debe usar las variables de entorno
    if PROJECT_ID == "":
        # Entregar el valor de la variable de entorno, si no esta definida, se entrega el valor por defecto
        value = os.getenv(secret_id.upper(), "")
        if value == "":
            return default
        return value

    # Obtener el project_id con la librería de Google Auth
    _, project_id = google.auth.default()

    # Si NO estamos en Google Cloud, entonces se está ejecutando de forma local
    if not project_id:
        # Entregar el valor de la variable de entorno, si no esta definida, se entrega el valor por defecto
        value = os.getenv(secret_id.upper())
        if value is None:
            return default
        return value

    # Tratar de obtener el secreto
    try:
        # Create the secret manager client
        client = secretmanager.SecretManagerServiceClient()
        # Build the resource name of the secret version
        secret = f"{SERVICE_PREFIX}_{secret_id}"
        name = client.secret_version_path(project_id, secret, "latest")
        # Access the secret version
        response = client.access_secret_version(name=name)
        # Return the decoded payload
        return response.payload.data.decode("UTF-8")
    except:
        pass

    # Entregar el valor por defecto porque no existe el secreto, ni la variable de entorno
    return default


class Settings(BaseSettings):
    """Settings"""

    FERNET_KEY: str = get_secret("FERNET_KEY")
    HOST: str = get_secret("HOST")
    REDIS_URL: str = get_secret("REDIS_URL")
    SALT: str = get_secret("SALT")
    SECRET_KEY: str = get_secret("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI: str = get_secret("SQLALCHEMY_DATABASE_URI")
    TASK_QUEUE: str = get_secret("TASK_QUEUE")
    TZ: str = get_secret("TZ", "America/Mexico_City")

    # Incrementar el tamaño de lo que se sube en los formularios
    MAX_CONTENT_LENGTH: int | None = None
    MAX_FORM_MEMORY_SIZE: int = 50 * MEGABYTE

    class Config:
        """Load configuration"""

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """Customise sources, first environment variables, then .env file, then google cloud secret manager"""
            return env_settings, file_secret_settings, init_settings


@lru_cache()
def get_settings() -> Settings:
    """Get Settings"""
    return Settings()
