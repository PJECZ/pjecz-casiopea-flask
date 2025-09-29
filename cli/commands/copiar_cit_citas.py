"""
Copiar tabla cit_citas de la base de datos ANTERIOR a la NUEVA

- copiar_cit_citas: Copiar tabla cit_citas de la base de datos ANTERIOR a la NUEVA
"""

import sys
import uuid

import click


def copiar_cit_citas(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla cit_citas de la base de datos ANTERIOR a la NUEVA"""
