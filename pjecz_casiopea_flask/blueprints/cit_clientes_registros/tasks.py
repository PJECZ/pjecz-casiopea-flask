"""
Cit Clientes Registros, tareas en el fondo
"""

from pjecz_casiopea_flask.blueprints.cit_clientes_registros.communications.send_to_sendgrid import enviar_a_sendgrid
from pjecz_casiopea_flask.lib.exceptions import MyAnyError
from pjecz_casiopea_flask.lib.tasks import set_task_error, set_task_progress


def lanzar_enviar_a_sendgrid(cit_cliente_registro_id: str) -> str:
    """Lanzar tarea en el fondo para para enviar a Sendgrid"""
    set_task_progress(0, "Se ha lanzado la tarea en el fondo para enviar a Sendgrid" "")
    try:
        mensaje_termino, _, _ = enviar_a_sendgrid(cit_cliente_registro_id)
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error
    set_task_progress(100, mensaje_termino)
    return mensaje_termino
