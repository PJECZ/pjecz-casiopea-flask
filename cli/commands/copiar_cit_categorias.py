"""
Copiar tabla cit_categorias de la base de datos ANTERIOR a la NUEVA

- copiar_cit_categorias: Copiar tabla cit_categorias de la base de datos ANTERIOR a la NUEVA
"""

import uuid

import click


def copiar_cit_categorias(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_categorias de la base de datos ANTERIOR a la NUEVA"""
