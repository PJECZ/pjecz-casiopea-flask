"""
Communications, enviar a Sendgrid un mensaje para terminar
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
from ..models import CitClienteRegistro
from . import bitacora

# Cargar variables de entorno
load_dotenv()
HOST = os.getenv("HOST", "http://localhost:5000")
NEW_ACCOUNT_CONFIRM_URL = os.getenv("NEW_ACCOUNT_CONFIRM_URL", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "")
TZ = os.getenv("TZ", "America/Mexico_City")

# Cargar la aplicación para tener acceso a la base de datos
app.app_context().push()


def enviar_a_sendgrid_mensaje_terminar(cit_cliente_registro_id: str) -> tuple[str, str, str]:
    """Enviar a Sendgrid un mensaje para terminar"""
    mensajes = []
    mensaje_info = "Inicia enviar a Sendgrid un mensaje para terminar"
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

    # Consultar el cit_cliente_registro
    cit_cliente_registro_id = safe_uuid(cit_cliente_registro_id)
    if not cit_cliente_registro_id:
        mensaje_error = "ID de registro inválido"
        bitacora.error(mensaje_error)
        raise MyNotValidParamError(mensaje_error)
    cit_cliente_registro = CitClienteRegistro.query.get(cit_cliente_registro_id)
    if not cit_cliente_registro:
        mensaje_error = "El registro no existe"
        bitacora.error(mensaje_error)
        raise MyNotExistsError(mensaje_error)

    # Validar el estatus, que no esté eliminado
    if cit_cliente_registro.estatus != "A":
        mensaje_error = "El registro está eliminado"
        bitacora.error(mensaje_error)
        raise MyIsDeletedError(mensaje_error)

    # Validar que ya haya completado su registro
    if cit_cliente_registro.ya_registrado is False:
        mensaje_error = "El cliente aun NO ha completado su registro"
        bitacora.error(mensaje_error)
        raise MyIsDeletedError(mensaje_error)

    # Elaborar el asunto del mensaje
    asunto_str = "Se ha completado el registro al Sistema de Citas PJECZ"

    # Elaborar el contenido del mensaje
    fecha_envio = datetime.now(tz=pytz.timezone(TZ)).strftime("%d/%b/%Y %H:%M")
    contenidos = []
    contenidos.append(f"<h2>{asunto_str}</h2>")
    contenidos.append(f"<p>Enviado el {fecha_envio}</p>")
    contenidos.append("<p><strong>Su cuenta está lista y ya puede ingresar al Sistema de Citas PJECZ</strong></p>")
    contenidos.append("<ul>")
    contenidos.append(f'<li><a href="{HOST}">{HOST}</a></li>')
    contenidos.append("</ul>")
    contenidos.append("<p>Use esta dirección de correo electrónico y su contraseña para ingresar.</p>")
    contenidos.append("<p>Este mensaje fue enviado por un programa. <em>NO RESPONDA ESTE MENSAJE.</em></p>")
    contenido_html = "\n".join(contenidos)

    # Enviar el e-mail
    send_grid = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    to_email = To(cit_cliente_registro.email)
    remitente_email = Email(SENDGRID_FROM_EMAIL)
    contenido = Content("text/html", contenido_html)
    mail = Mail(
        from_email=remitente_email,
        to_emails=to_email,
        subject=asunto_str,
        html_content=contenido,
    )

    # Enviar mensaje de correo electrónico
    try:
        send_grid.send(mail)
    except Exception as error:
        mensaje_error = f"Error al enviar el mensaje por Sendgrid: {str(error)}"
        bitacora.error(mensaje_error)
        raise MyRequestError(mensaje_error)

    # Elaborar mensaje_termino
    mensaje_termino = f"Se ha enviado un mensaje por Sendgrid a {cit_cliente_registro.email} para confirmar."
    mensajes.append(mensaje_termino)
    bitacora.info(mensaje_termino)

    # Entregar mensaje_termino, nombre_archivo y url_publica
    return "\n".join(mensajes), "", ""
