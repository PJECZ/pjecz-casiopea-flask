"""
CIT Cit Clientes Registros

- eliminar: Eliminar registros
- enviar: Enviar mensaje de correo electrónico por SendGrid para validar
- reenviar: Reenviar mensajes a quienes no han terminado su registro
"""

import os
import sys

import click
import rq
from dotenv import load_dotenv
from redis import ConnectionPool, Redis

# Cargar variables de entorno
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "http://localhost:6379")
TASK_QUEUE = os.getenv("TASK_QUEUE", "pjecz_casiopea")


@click.group()
def cli():
    """Cit Clientes Registros"""


@click.command()
@click.argument("cit_cliente_registro_id", type=str)
def enviar(cit_cliente_registro_id):
    """Enviar mensaje de correo electrónico por SendGrid para validar"""

    # Obtener la conexión a Redis
    pool = ConnectionPool.from_url(url=REDIS_URL)
    if not pool:
        click.echo(click.style("ERROR: No se pudo conectar a Redis", fg="red"))
        sys.exit(1)
    redis_conn = Redis(connection_pool=pool)
    if not redis_conn:
        click.echo(click.style("ERROR: No se pudo conectar a Redis", fg="red"))
        sys.exit(1)

    # Crear la cola de tareas
    task_queue = rq.Queue(name=TASK_QUEUE, connection=redis_conn)

    # Lanzar la tarea
    rq_job = task_queue.enqueue(
        "pjecz_casiopea_flask.blueprints.cit_clientes_registros.tasks.lanzar_enviar_a_sendgrid",
        cit_cliente_registro_id=cit_cliente_registro_id,
    )
    if not rq_job:
        click.echo(click.style("ERROR: No se pudo lanzar la tarea en el fondo", fg="red"))
        sys.exit(1)

    click.echo(f"Se lanzado la tarea en el fondo {rq_job.id} para enviar un mensaje por Sendgrid")


cli.add_command(enviar)
