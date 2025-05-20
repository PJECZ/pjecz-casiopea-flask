"""
CLI Base de Datos

- cambiar_contrasena: Cambiar contraseña de un cliente
"""

import os
import sys

import click
from dotenv import load_dotenv

from cli.commands.alimentar_autoridades import alimentar_autoridades
from cli.commands.alimentar_cit_dias_inhabiles import alimentar_cit_dias_inhabiles
from cli.commands.alimentar_cit_oficinas_servicios import alimentar_cit_oficinas_servicios
from cli.commands.alimentar_cit_servicios import alimentar_cit_servicios
from cli.commands.alimentar_distritos import alimentar_distritos
from cli.commands.alimentar_domicilios import alimentar_domicilios
from cli.commands.alimentar_materias import alimentar_materias
from cli.commands.alimentar_modulos import alimentar_modulos
from cli.commands.alimentar_oficinas import alimentar_oficinas
from cli.commands.alimentar_roles import alimentar_roles
from cli.commands.alimentar_permisos import alimentar_permisos
from cli.commands.alimentar_usuarios import alimentar_usuarios
from cli.commands.alimentar_usuarios_roles import alimentar_usuarios_roles
from pjecz_casiopea_flask.main import app
from pjecz_casiopea_flask.config.extensions import database

app.app_context().push()
database.app = app

load_dotenv()  # Take environment variables from .env
DEPLOYMENT_ENVIRONMENT = os.environ.get("DEPLOYMENT_ENVIRONMENT", "develop").upper()


@click.group()
def cli():
    """Base de Datos"""


@click.command()
def inicializar():
    """Inicializar"""
    if DEPLOYMENT_ENVIRONMENT == "PRODUCTION":
        click.echo("PROHIBIDO: No se inicializa porque este es el servidor de producción.")
        sys.exit(1)
    database.drop_all()
    database.create_all()
    click.echo("Termina inicializar.")


@click.command()
def alimentar():
    """Alimentar"""
    if DEPLOYMENT_ENVIRONMENT == "PRODUCTION":
        click.echo("PROHIBIDO: No se alimenta porque este es el servidor de producción.")
        sys.exit(1)
    alimentar_materias()
    alimentar_distritos()
    alimentar_autoridades()
    alimentar_modulos()
    alimentar_roles()
    alimentar_permisos()
    alimentar_usuarios()
    alimentar_usuarios_roles()
    alimentar_domicilios()
    alimentar_oficinas()
    alimentar_cit_servicios()
    alimentar_cit_oficinas_servicios()
    alimentar_cit_dias_inhabiles()
    click.echo("Termina alimentar.")


@click.command()
@click.pass_context
def reiniciar(ctx):
    """Reiniciar ejecuta inicializar y alimentar"""
    ctx.invoke(inicializar)
    ctx.invoke(alimentar)


@click.command()
def respaldar():
    """Respaldar"""
    click.echo("Termina respaldar.")


cli.add_command(inicializar)
cli.add_command(alimentar)
cli.add_command(reiniciar)
cli.add_command(respaldar)
