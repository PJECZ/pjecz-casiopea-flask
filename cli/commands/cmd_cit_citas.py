"""
CLI Cit Citas
"""

import random
import sys
from datetime import datetime, timedelta

import click
from faker import Faker
from sqlalchemy.sql import func

from pjecz_casiopea_flask.blueprints.cit_citas.models import CitCita
from pjecz_casiopea_flask.blueprints.cit_clientes.models import CitCliente
from pjecz_casiopea_flask.blueprints.cit_oficinas_servicios.models import CitOficinaServicio
from pjecz_casiopea_flask.blueprints.cit_servicios.models import CitServicio
from pjecz_casiopea_flask.blueprints.oficinas.models import Oficina
from pjecz_casiopea_flask.main import app

app.app_context().push()


@click.group()
def cli():
    """Cit Citas"""


@click.command()
@click.option("--maximo", default=3, help="Máximo de citas a agregar por cliente")
@click.option("--desde", help="Fecha desde AAAA-MM-DD")
@click.option("--hasta", help="Fecha hasta AAAA-MM-DD")
def agregar_falsos(maximo, desde, hasta):
    """Agregar citas con datos falsos"""
    # Si no viene desde, usar el día de hoy
    if not desde:
        desde_dt = datetime.now().date()
    else:
        try:
            desde_dt = datetime.strptime(desde, "%Y-%m-%d").date()
        except ValueError:
            click.echo(click.style("Fecha 'desde' inválida", fg="red"))
            sys.exit(1)
    # Si no viene hasta, usar 30 días después del día de hoy
    if not hasta:
        hasta_dt = datetime.now().date() + timedelta(days=30)
    else:
        try:
            hasta_dt = datetime.strptime(hasta, "%Y-%m-%d").date()
        except ValueError:
            click.echo(click.style("Fecha 'hasta' inválida", fg="red"))
            sys.exit(1)
    # Consultar cit_clientes
    cit_clientes = CitCliente.query.filter(CitCliente.estatus == "A").all()
    # Si no hay cit_clientes, salir
    if not cit_clientes:
        click.echo(click.style("No hay cit_clientes para asignar citas", fg="red"))
        sys.exit(1)
    # Inicializar el contador
    contador = 0
    # Bucle entre los cit_clientes
    for cit_cliente in cit_clientes:
        click.echo(f"- {cit_cliente.email}: ", nl=False)
        # Bucle para agregar citas, de una a LIMITE_CITAS_CANTIDAD
        for _ in range(1, random.randint(1, maximo) + 1):
            # Definir una fecha aleatoria entre desde_dt y hasta_dt
            delta_dias = (hasta_dt - desde_dt).days
            fecha = desde_dt + timedelta(days=random.randint(0, delta_dias))
            # Definir una hora aleatoria entre 9:00 y 12:00
            hora = random.randint(9, 11)
            minuto = random.choice([0, 15, 30, 45])
            fecha_hora = datetime(fecha.year, fecha.month, fecha.day, hora, minuto)
            # Bucle hasta encontrar un servicio y oficina
            while True:
                # Consultar un CitServicio aleatorio
                cit_servicio = CitServicio.query.order_by(func.random()).first()
                if cit_servicio is None:
                    click.echo(click.style("No hay servicios para asignar citas", fg="red"))
                    sys.exit(1)
                # Consultar una Oficina aleatoria
                oficina = Oficina.query.order_by(func.random()).first()
                if oficina is None:
                    click.echo(click.style("No hay oficinas para asignar citas", fg="red"))
                    sys.exit(1)
                # Consultar si hay un CitOficinaServicio para el servicio y oficina
                cit_oficina_servicio = CitOficinaServicio.query.filter_by(
                    cit_servicio_id=cit_servicio.id,
                    oficina_id=oficina.id,
                ).first()
                # Si lo hay, salir el bucle
                if cit_oficina_servicio:
                    break
            # Crear la cita
            cit_cita = CitCita()
            cit_cita.cit_cliente_id = cit_cliente.id
            cit_cita.cit_servicio_id = cit_servicio.id
            cit_cita.oficina_id = oficina.id
            cit_cita.inicio = fecha_hora
            cit_cita.termino = fecha_hora + timedelta(hours=cit_servicio.duracion.hour, minutes=cit_servicio.duracion.minute)
            cit_cita.notas = Faker().sentence(nb_words=6)
            cit_cita.estado = "PENDIENTE"
            cit_cita.cancelar_antes = cit_cita.inicio - timedelta(hours=24)
            cit_cita.asistencia = False
            cit_cita.codigo_asistencia = "".join(random.choices("0123456789", k=6))
            cit_cita.save()
            # Mostrar un signo + en verde
            click.echo(click.style("+", fg="green"), nl=False)
            contador += 1
        click.echo()
    # Mensaje final
    click.echo(f"Se han agregado {contador} citas falsas")


@click.command()
@click.option("--horas", type=int, default=24, help="Eliminar los que tengan más de este tiempo")
def eliminar(horas):
    """Eliminar citas pasadas"""
    # Definir el tiempo límite
    tiempo_limite = datetime.now() - timedelta(hours=horas)
    # Consultar las citas a eliminar
    citas = CitCita.query.filter(CitCita.inicio < tiempo_limite).filter(CitCita.estatus == "A").all()
    # Contador
    contador = 0
    # Bucle entre las citas
    for cita in citas:
        cita.delete()
        contador += 1
    # Mensaje final
    click.echo(f"Se han eliminado {contador} citas pasadas de más de {horas} horas")


cli.add_command(agregar_falsos)
cli.add_command(eliminar)
