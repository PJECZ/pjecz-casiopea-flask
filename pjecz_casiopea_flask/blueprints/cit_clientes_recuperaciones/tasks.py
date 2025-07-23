"""
Cit Clientes Recuperaciones, tareas en el fondo
"""

from ...lib.exceptions import MyAnyError
from ...lib.tasks import set_task_error, set_task_progress
from .communications.send_to_sendgrid_email_terminate import enviar_a_sendgrid_mensaje_terminar
from .communications.send_to_sendgrid_email_validate import enviar_a_sendgrid_mensaje_validar


def lanzar_enviar_a_sendgrid_mensaje_terminar(cit_cliente_registro_id: str) -> str:
    """Lanzar tarea en el fondo para enviar a Sendgrid un mensaje para terminar"""
    set_task_progress(0, "Se ha lanzado la tarea en el fondo para enviar a Sendgrid un mensaje para terminar")
    try:
        mensaje_termino, _, _ = enviar_a_sendgrid_mensaje_terminar(cit_cliente_registro_id)
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error
    set_task_progress(100, mensaje_termino)
    return mensaje_termino


def lanzar_enviar_a_sendgrid_mensaje_validar(cit_cliente_registro_id: str) -> str:
    """Lanzar tarea en el fondo para enviar a Sendgrid un mensaje para validar"""
    set_task_progress(0, "Se ha lanzado la tarea en el fondo para enviar a Sendgrid un mensaje para validar")
    try:
        mensaje_termino, _, _ = enviar_a_sendgrid_mensaje_validar(cit_cliente_registro_id)
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error
    set_task_progress(100, mensaje_termino)
    return mensaje_termino
