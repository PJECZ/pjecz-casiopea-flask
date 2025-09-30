"""
Copiar tabla cit_oficinas_servicios de la base de datos ANTERIOR a la NUEVA

- copiar_cit_oficinas_servicios: Copiar tabla cit_oficinas_servicios de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_oficinas_servicios(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_oficinas_servicios de la base de datos ANTERIOR a la NUEVA"""
