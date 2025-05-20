"""
CLI Cit Clientes

- agregar_falsos: Agregar clientes con datos falsos
- cambiar_contrasena: Cambiar la contraseña de un cliente
"""

from datetime import datetime, timedelta
import random
import sys

import click
from faker import Faker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from pjecz_casiopea_flask.blueprints.cit_clientes.models import CitCliente
from pjecz_casiopea_flask.config.extensions import database, pwd_context
from pjecz_casiopea_flask.lib.curp_generator import generar_curp_falso, generar_nacimiento_falso
from pjecz_casiopea_flask.lib.pwgen import generar_contrasena
from pjecz_casiopea_flask.lib.safe_string import safe_email, safe_string
from pjecz_casiopea_flask.main import app

app.app_context().push()
database.app = app


@click.group()
def cli():
    """Cit Clientes"""


@click.command()
@click.option("--cantidad", default=10, help="Cantidad de clientes falsos a agregar")
def agregar_falsos(cantidad):
    """Agregar clientes con datos falsos"""
    faker = Faker(locale="es_MX")
    for _ in range(1, cantidad + 1):
        nombres = safe_string(faker.first_name(), save_enie=True)
        apellido_primero = safe_string(faker.last_name(), save_enie=True)
        apellido_segundo = safe_string(faker.last_name(), save_enie=True)
        contrasena = generar_contrasena()
        cit_cliente = CitCliente(
            nombres=nombres,
            apellido_primero=apellido_primero,
            apellido_segundo=apellido_segundo,
            curp=generar_curp_falso(nombres, apellido_primero, apellido_segundo, generar_nacimiento_falso()),
            telefono="".join(random.choices("0123456789", k=10)),
            email=faker.safe_email(),
            contrasena_md5="",
            contrasena_sha256=pwd_context.hash(contrasena),
            renovacion=datetime.now() + timedelta(days=60),
            limite_citas_pendientes=5,
        )
        cit_cliente.save()
        click.echo(f"+ {cit_cliente.email}: {contrasena}")
    click.echo(f"Se han agregado {cantidad} clientes falsos")


@click.command()
@click.argument("email", type=str)
def cambiar_contrasena(email):
    """Cambiar la contraseña de un cliente"""
    # Validar email
    try:
        email = safe_email(email)
    except ValueError:
        click.echo("No es válido el email")
        sys.exit(1)
    # Consultar
    try:
        cit_cliente = CitCliente.query.filter_by(email=email).one()
    except (MultipleResultsFound, NoResultFound):
        click.echo("No se encontró el cliente")
        sys.exit(1)
    # Generar contraseña
    contrasena = generar_contrasena()
    cit_cliente.contrasena_md5 = ""
    cit_cliente.contrasena_sha256 = pwd_context.hash(contrasena)
    cit_cliente.renovacion = datetime.now() + timedelta(days=60)
    cit_cliente.save()
    # Mostrar
    click.echo(f"Se ha cambiado la contraseña de {email} a {contrasena}")


cli.add_command(agregar_falsos)
cli.add_command(cambiar_contrasena)
