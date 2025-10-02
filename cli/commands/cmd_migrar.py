"""
Migrar la base de datos

- copiar: Copiar los registros de la base de datos ANTERIOR a la NUEVA
"""

import os
import sys

import click
import psycopg2
from dotenv import load_dotenv

from cli.commands.copiar_autoridades import copiar_autoridades
from cli.commands.copiar_cit_categorias import copiar_cit_categorias
from cli.commands.copiar_cit_citas import copiar_cit_citas
from cli.commands.copiar_cit_clientes import copiar_cit_clientes
from cli.commands.copiar_cit_clientes_recuperaciones import copiar_cit_clientes_recuperaciones
from cli.commands.copiar_cit_clientes_registros import copiar_cit_clientes_registros
from cli.commands.copiar_cit_oficinas_servicios import copiar_cit_oficinas_servicios
from cli.commands.copiar_cit_servicios import copiar_cit_servicios
from cli.commands.copiar_distritos import copiar_distritos
from cli.commands.copiar_domicilios import copiar_domicilios
from cli.commands.copiar_oficinas import copiar_oficinas
from cli.commands.copiar_pag_pagos import copiar_pag_pagos
from cli.commands.copiar_pag_tramites_servicios import copiar_pag_tramites_servicios

load_dotenv()  # Take environment variables from .env

# Cargar variables de entorno para la base de datos ANTERIOR
OLD_DB_NAME = os.environ.get("OLD_DB_NAME")
OLD_DB_USER = os.environ.get("OLD_DB_USER")
OLD_DB_PASS = os.environ.get("OLD_DB_PASS")
OLD_DB_HOST = os.environ.get("OLD_DB_HOST")
OLD_DB_PORT = os.environ.get("OLD_DB_PORT")

# Cargar variables de entorno para la base de datos NUEVA
NEW_DB_NAME = os.environ.get("NEW_DB_NAME")
NEW_DB_USER = os.environ.get("NEW_DB_USER")
NEW_DB_PASS = os.environ.get("NEW_DB_PASS")
NEW_DB_HOST = os.environ.get("NEW_DB_HOST")
NEW_DB_PORT = os.environ.get("NEW_DB_PORT")


@click.group()
def cli():
    """Migrar"""


@click.command()
def copiar():
    """Copiar registros de la base de datos ANTERIOR a la NUEVA"""
    try:
        # Conectar a la base de datos ANTERIOR
        conn_old = psycopg2.connect(
            dbname=OLD_DB_NAME,
            user=OLD_DB_USER,
            password=OLD_DB_PASS,
            host=OLD_DB_HOST,
            port=OLD_DB_PORT,
        )
        cursor_old = conn_old.cursor()
    except Exception as error:
        click.echo(click.style(f"Error al conectar a la BD ANTERIOR: {error}", fg="red"))
        sys.exit(1)
    try:
        # Conectar a la base de datos NUEVA
        conn_new = psycopg2.connect(
            dbname=NEW_DB_NAME,
            user=NEW_DB_USER,
            password=NEW_DB_PASS,
            host=NEW_DB_HOST,
            port=NEW_DB_PORT,
        )
        cursor_new = conn_new.cursor()
    except Exception as e:
        click.echo(click.style(f"Error al conectar a la BD NUEVA: {e}", fg="red"))
        sys.exit(1)
    # Ejecutar las copias en el orden correcto
    try:
        copiar_distritos(conn_old, cursor_old, conn_new, cursor_new)
        copiar_autoridades(conn_old, cursor_old, conn_new, cursor_new)
        copiar_domicilios(conn_old, cursor_old, conn_new, cursor_new)
        copiar_oficinas(conn_old, cursor_old, conn_new, cursor_new)
        copiar_cit_categorias(conn_old, cursor_old, conn_new, cursor_new)
        copiar_cit_servicios(conn_old, cursor_old, conn_new, cursor_new)
        copiar_cit_oficinas_servicios(conn_old, cursor_old, conn_new, cursor_new)
        copiar_cit_clientes(conn_old, cursor_old, conn_new, cursor_new)
        copiar_cit_clientes_recuperaciones(conn_old, cursor_old, conn_new, cursor_new)
        copiar_cit_clientes_registros(conn_old, cursor_old, conn_new, cursor_new)
        copiar_cit_citas(conn_old, cursor_old, conn_new, cursor_new)
        copiar_pag_tramites_servicios(conn_old, cursor_old, conn_new, cursor_new)
        copiar_pag_pagos(conn_old, cursor_old, conn_new, cursor_new)
    except Exception as error:
        click.echo(click.style(error, fg="red"))
        sys.exit(1)
    # Cerrar las conexiones (si no se cerraron ya en las funciones)
    try:
        cursor_old.close()
        conn_old.close()
        cursor_new.close()
        conn_new.close()
    except Exception:
        pass


cli.add_command(copiar)
