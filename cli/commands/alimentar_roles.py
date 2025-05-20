"""
Alimentar Roles
"""

import csv
import sys
from pathlib import Path

import click

from pjecz_casiopea_flask.blueprints.roles.models import Rol
from pjecz_casiopea_flask.lib.safe_string import safe_string

ROLES_CSV = "seed/roles_permisos.csv"


def alimentar_roles():
    """Alimentar Roles"""
    ruta = Path(ROLES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando roles: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            nombre = safe_string(row.get("rol_nombre"), save_enie=True)
            estatus = row.get("estatus")
            Rol(
                nombre=nombre,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} roles alimentados.", fg="green"))
