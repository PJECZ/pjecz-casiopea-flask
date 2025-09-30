"""
Copiar tabla pag_pagos de la base de datos ANTERIOR a la NUEVA

- copiar_pag_pagos: Copiar tabla pag_pagos de la base de datos ANTERIOR a la NUEVA
"""

import sys
import uuid

import click


def copiar_pag_pagos(conn_old, cursor_old, conn_new, cursor_new):
    """Copiar tabla pag_pagos de la base de datos ANTERIOR a la NUEVA"""
    click.echo(click.style(f"  Falta programar copiar pag_pagos.", fg="yellow"))
