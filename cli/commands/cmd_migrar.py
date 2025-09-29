"""
Migrar la base de datos

- copiar: Copiar los registros de la base de datos ANTERIOR a la NUEVA
"""

import os
import sys

import click
import psycopg2
from dotenv import load_dotenv

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
    # Ejecutar las copias
    copiar_pag_tramites_servicios(conn_old, cursor_old, conn_new, cursor_new)


cli.add_command(copiar)
