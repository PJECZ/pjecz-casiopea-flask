"""
Copiar tabla cit_clientes_registros de la base de datos ANTERIOR a la NUEVA

- copiar_cit_clientes_registros: Copiar tabla cit_clientes_registros de la base de datos ANTERIOR a la NUEVA
"""

import sys
import uuid

import click


def copiar_cit_clientes_registros(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_clientes_registros de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style(f"  Falta programar copiar cit_clientes_registros.", fg="yellow"))
