"""
Communications, enviar a Sendgrid un mensaje para nueva contraseña
"""

import os
from datetime import datetime

import pytz
import sendgrid
from dotenv import load_dotenv
from sendgrid.helpers.mail import Content, Email, Mail, To

from pjecz_casiopea_flask.lib.safe_string import safe_uuid
from pjecz_casiopea_flask.main import app

from ....lib.exceptions import (
    MyIsDeletedError,
    MyMissingConfigurationError,
    MyNotExistsError,
    MyNotValidParamError,
    MyRequestError,
)
from ..models import CitClienteRecuperacion
from . import bitacora

# Cargar variables de entorno
load_dotenv()
NEW_ACCOUNT_CONFIRM_URL = os.getenv("NEW_ACCOUNT_CONFIRM_URL", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "")
TZ = os.getenv("TZ", "America/Mexico_City")

# Cargar la aplicación para tener acceso a la base de datos
app.app_context().push()


def enviar_a_sendgrid_mensaje_validar(cit_cliente_recuperacion_id: str) -> tuple[str, str, str]:
    """Enviar a Sendgrid un mensaje para validar"""
    mensajes = []
    mensaje_info = "Inicia enviar a Sendgrid un mensaje para validar"
    mensajes.append(mensaje_info)
    bitacora.info(mensaje_info)

    # Validar que esté definida la variable de entorno NEW_ACCOUNT_CONFIRM_URL
    if not NEW_ACCOUNT_CONFIRM_URL:
        mensaje_error = "La variable de entorno NEW_ACCOUNT_CONFIRM_URL no está definida"
        bitacora.error(mensaje_error)
        raise MyMissingConfigurationError(mensaje_error)

    # Validar que esté definida la variable de entorno SENDGRID_API_KEY
    if not SENDGRID_API_KEY:
        mensaje_error = "La variable de entorno SENDGRID_API_KEY no está definida"
        bitacora.error(mensaje_error)
        raise MyMissingConfigurationError(mensaje_error)

    # Validar que esté definida la variable de entorno SENDGRID_FROM_EMAIL
    if not SENDGRID_FROM_EMAIL:
        mensaje_error = "La variable de entorno SENDGRID_FROM_EMAIL no está definida"
        bitacora.error(mensaje_error)
        raise MyMissingConfigurationError(mensaje_error)

    # Consultar el cit_cliente_recuperacion
    cit_cliente_recuperacion_id = safe_uuid(cit_cliente_recuperacion_id)
    if not cit_cliente_recuperacion_id:
        mensaje_error = "ID del cliente inválido"
        bitacora.error(mensaje_error)
        raise MyNotValidParamError(mensaje_error)
    cit_cliente_recuperacion = CitClienteRecuperacion.query.get(cit_cliente_recuperacion_id)
    if not cit_cliente_recuperacion:
        mensaje_error = "El cliente no existe"
        bitacora.error(mensaje_error)
        raise MyNotExistsError(mensaje_error)

    # Validar el estatus, que no esté eliminado
    if cit_cliente_recuperacion.estatus != "A":
        mensaje_error = "El cliente está eliminado"
        bitacora.error(mensaje_error)
        raise MyIsDeletedError(mensaje_error)

    # Entregar mensaje_termino, nombre_archivo y url_publica
    return "\n".join(mensajes), "", ""
