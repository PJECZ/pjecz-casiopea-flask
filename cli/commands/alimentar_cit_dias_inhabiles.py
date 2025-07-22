"""
Alimentar Cit Días Inhábiles
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

import click
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pjecz_casiopea_flask.blueprints.cit_dias_inhabiles.models import CitDiaInhabil
from pjecz_casiopea_flask.lib.safe_string import safe_string

CIT_DIAS_INHABILES_CSV = "seed/cit_dias_inhabiles.csv"


def alimentar_cit_dias_inhabiles():
    """Alimentar Cit Dias Inhabiles"""
    ruta = Path(CIT_DIAS_INHABILES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando cit_dias_inhabiles: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            try:
                fecha = datetime.strptime(row.get("fecha"), "%Y-%m-%d")
            except ValueError:
                click.echo(f"No es válida la fecha {row['fecha']}")
                sys.exit(1)
            descripcion = safe_string(row.get("descripcion"), save_enie=True)
            estatus = row.get("estatus")
            CitDiaInhabil(
                fecha=fecha,
                descripcion=descripcion,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} cit_dias_inhabiles alimentados.", fg="green"))
