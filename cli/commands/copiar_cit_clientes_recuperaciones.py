"""
Copiar tabla cit_clientes_recuperaciones de la base de datos ANTERIOR a la NUEVA

- copiar_cit_clientes_recuperaciones: Copiar tabla cit_clientes_recuperaciones de la base de datos ANTERIOR a la NUEVA
"""

import sys
import uuid

import click


def copiar_cit_clientes_recuperaciones(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_clientes_recuperaciones de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style(f"  Falta programar copiar cit_clientes_recuperaciones.", fg="yellow"))
