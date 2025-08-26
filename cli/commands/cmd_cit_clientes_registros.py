"""
CIT Cit Clientes Registros

- eliminar: Eliminar registros
- enviar: Enviar mensaje de correo electrónico por SendGrid para validar
- reenviar: Reenviar mensajes a quienes no han terminado su registro
"""

import os
import sys
from datetime import datetime, timedelta

import click
import rq
from dotenv import load_dotenv
from redis import ConnectionPool, Redis

from pjecz_casiopea_flask.blueprints.cit_clientes_registros.models import CitClienteRegistro
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
    """Cit Clientes Registros"""


@click.command()
@click.option("--horas", type=int, default=48, help="Eliminar los que tengan más de este tiempo")
def eliminar(horas):
    """Eliminar registros"""
    # Consultar los CitClienteRegistro cuyo tiempo de creación sea mayor a las horas especificadas
    tiempo_limite = datetime.now() - timedelta(hours=horas)
    registros = (
        CitClienteRegistro.query.filter(CitClienteRegistro.creado < tiempo_limite)
        .filter(CitClienteRegistro.estatus == "A")
        .all()
    )
    if not registros:
        click.echo("No hay registros para eliminar")
        sys.exit(0)
    # Eliminar los registros
    for registro in registros:
        registro.delete()
    click.echo(f"Se han eliminado {len(registros)} registros antiguos de más de {horas} horas")


@click.command()
@click.argument("cit_cliente_registro_id", type=str)
def enviar(cit_cliente_registro_id):
    """Enviar mensaje de correo electrónico por SendGrid para validar"""
    rq_job = get_task_queue().enqueue(
        "pjecz_casiopea_flask.blueprints.cit_clientes_registros.tasks.lanzar_enviar_a_sendgrid",
        cit_cliente_registro_id=cit_cliente_registro_id,
    )
    if not rq_job:
        click.echo(click.style("ERROR: No se pudo lanzar la tarea en el fondo", fg="red"))
        sys.exit(1)
    click.echo(f"Se lanzado la tarea en el fondo {rq_job.id} para enviar un mensaje por Sendgrid para validar")


@click.command()
def reenviar():
    """Reenviar mensajes a quienes no han terminado su registro"""
    # Consultar los CitClienteRegistro cuyo ya_registrado sea False y estatus sea "A"
    registros = CitClienteRegistro.query.filter_by(ya_registrado=False).filter_by(estatus="A").all()
    if not registros:
        click.echo("No hay registros para reenviar")
        sys.exit(0)
    # Reenviar los mensajes
    task_queue = get_task_queue()
    for registro in registros:
        rq_job = task_queue.enqueue(
            "pjecz_casiopea_flask.blueprints.cit_clientes_registros.tasks.lanzar_enviar_a_sendgrid",
            cit_cliente_registro_id=registro.id,
        )
        if not rq_job:
            click.echo(click.style(f"ERROR: No se pudo lanzar la tarea en el fondo para {registro.id}", fg="red"))
            continue
    click.echo(f"Se han lanzado {len(registros)} tareas en el fondo para reenviar mensajes a los registros pendientes")


cli.add_command(eliminar)
cli.add_command(enviar)
cli.add_command(reenviar)
