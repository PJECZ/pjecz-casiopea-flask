"""
Alimentar Materias
"""

import csv
import sys
from pathlib import Path

import click

from pjecz_casiopea_flask.blueprints.materias.models import Materia
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string

MATERIAS_CSV = "seed/materias.csv"


def alimentar_materias():
    """Alimentar Materias"""
    ruta = Path(MATERIAS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando materias: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            clave = safe_clave(row.get("clave"))
            nombre = safe_string(row.get("nombre"), save_enie=True)
            descripcion = safe_string(row.get("descripcion"), save_enie=True)
            estatus = row.get("estatus")
            Materia(
                clave=clave,
                nombre=nombre,
                descripcion=descripcion,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} materias alimentadas.", fg="green"))
