"""
Alimentar Permisos
"""

import csv
import sys
from pathlib import Path

import click

from pjecz_casiopea_flask.blueprints.modulos.models import Modulo
from pjecz_casiopea_flask.blueprints.permisos.models import Permiso
from pjecz_casiopea_flask.blueprints.roles.models import Rol
from pjecz_casiopea_flask.lib.safe_string import safe_string

PERMISOS_CSV = "seed/roles_permisos.csv"


def alimentar_permisos():
    """Alimentar Permisos"""
    ruta = Path(PERMISOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    modulos = Modulo.query.order_by(Modulo.nombre).all()
    click.echo("Alimentando permisos: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            rol_nombre = safe_string(row.get("rol_nombre"), save_enie=True)
            estatus = row["estatus"]
            rol = Rol.query.filter(Rol.nombre == rol_nombre).first()
            if rol is None:
                click.echo(click.style(f"  AVISO: rol {rol_nombre} no existe", fg="red"))
                sys.exit(1)
            for modulo in modulos:
                columna = modulo.nombre.lower()
                if columna not in row:
                    continue
                if row[columna] == "":
                    continue
                try:
                    nivel = int(row.get(columna))
                except ValueError:
                    nivel = 0
                if nivel < 0:
                    nivel = 0
                if nivel > 4:
                    nivel = 4
                Permiso(
                    rol=rol,
                    modulo=modulo,
                    nivel=nivel,
                    nombre=f"{rol.nombre} puede {Permiso.NIVELES[nivel]} en {modulo.nombre}",
                    estatus=estatus,
                ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} permisos alimentados.", fg="green"))
