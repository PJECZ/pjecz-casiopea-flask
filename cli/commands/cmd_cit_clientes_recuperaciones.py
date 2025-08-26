"""
CLI Cit Clientes Recuperaciones

- eliminar: Eliminar recuperaciones
- enviar: Enviar mensaje de correo electrónico por SendGrid para validar
- reenviar: Reenviar mensajes a quienes no han terminado su recuperación
"""

import os
import sys
from datetime import datetime, timedelta

import click
import rq
from dotenv import load_dotenv
from redis import ConnectionPool, Redis

from pjecz_casiopea_flask.blueprints.cit_clientes_recuperaciones.models import CitClienteRecuperacion
from pjecz_casiopea_flask.main import app

# Cargar variables de entorno
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "http://localhost:6379")
TASK_QUEUE = os.getenv("TASK_QUEUE", "pjecz_casiopea")

# Cargar la aplicación para tener acceso a la base de datos
app.app_context().push()


def get_task_queue():
    """Obtener la cola de tareas"""
    pool = ConnectionPool.from_url(url=REDIS_URL)
    if not pool:
        click.echo(click.style("ERROR: No se pudo conectar a Redis", fg="red"))
        sys.exit(1)
    redis_conn = Redis(connection_pool=pool)
    if not redis_conn:
        click.echo(click.style("ERROR: No se pudo conectar a Redis", fg="red"))
        sys.exit(1)
    return rq.Queue(name=TASK_QUEUE, connection=redis_conn)


@click.group()
def cli():
    """Cit Clientes Recuperaciones"""


@click.command()
@click.option("--horas", type=int, default=48, help="Eliminar los que tengan más de este tiempo")
def eliminar(horas):
    """Eliminar recuperaciones"""
    # Consultar los CitClienteRecuperaciones cuyo tiempo de creación sea mayor a las horas especificadas
    tiempo_limite = datetime.now() - timedelta(hours=horas)
    recuperaciones = (
        CitClienteRecuperacion.query.filter(CitClienteRecuperacion.creado < tiempo_limite)
        .filter(CitClienteRecuperacion.estatus == "A")
        .all()
    )
    if not recuperaciones:
        click.echo("No hay recuperaciones para eliminar")
        sys.exit(0)
    # Eliminar las recuperaciones
    for recuperacion in recuperaciones:
        recuperacion.delete()
    click.echo(f"Se han eliminado {len(recuperaciones)} recuperaciones antiguas de más de {horas} horas")


@click.command()
@click.argument("cit_cliente_recuperacion_id", type=str)
def enviar(cit_cliente_recuperacion_id):
    """Enviar mensaje de correo electrónico por SendGrid para validar"""
    rq_job = get_task_queue().enqueue(
        "pjecz_casiopea_flask.blueprints.cit_clientes_recuperaciones.tasks.lanzar_enviar_a_sendgrid_mensaje_validar",
        cit_cliente_recuperacion_id=cit_cliente_recuperacion_id,
    )
    if not rq_job:
        click.echo(click.style("ERROR: No se pudo lanzar la tarea en el fondo", fg="red"))
        sys.exit(1)
    click.echo(f"Se lanzado la tarea en el fondo {rq_job.id} para enviar un mensaje por Sendgrid para validar")


@click.command()
@click.argument("cit_cliente_recuperacion_id", type=str)
def reenviar(cit_cliente_recuperacion_id):
    """Reenviar mensajes a quienes no han terminado su recuperación"""
    # Consultar los CitClienteRecuperacion cuyo ya_recuperado sea False y estatus sea "A"
    recuperaciones = CitClienteRecuperacion.query.filter_by(ya_recuperado=False).filter_by(estatus="A").all()
    if not recuperaciones:
        click.echo("No hay recuperaciones para reenviar")
        sys.exit(0)
    # Reenviar los mensajes
    task_queue = get_task_queue()
    for recuperacion in recuperaciones:
        rq_job = task_queue.enqueue(
            "pjecz_casiopea_flask.blueprints.cit_clientes_recuperaciones.tasks.lanzar_enviar_a_sendgrid_mensaje_validar",
            cit_cliente_recuperacion_id=recuperacion.id,
        )
        if not rq_job:
            click.echo(click.style("ERROR: No se pudo lanzar la tarea en el fondo", fg="red"))
            sys.exit(1)
    click.echo(f"Se han reenviado {len(recuperaciones)} mensajes a quienes no han terminado su recuperación")


cli.add_command(eliminar)
cli.add_command(enviar)
cli.add_command(reenviar)
