"""
Alimentar Distritos
"""

import csv
import sys
from pathlib import Path

import click

from pjecz_casiopea_flask.blueprints.distritos.models import Distrito
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string

DISTRITOS_CSV = "seed/distritos.csv"


def alimentar_distritos():
    """Alimentar Distritos"""
    ruta = Path(DISTRITOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando distritos: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            clave = safe_clave(row.get("clave"))
            nombre = safe_string(row.get("nombre"), save_enie=True)
            nombre_corto = safe_string(row.get("nombre_corto"), save_enie=True)
            es_activo = row.get("es_activo") == "1"
            es_distrito_judicial = row.get("es_distrito_judicial") == "1"
            es_distrito = row.get("es_distrito_judicial") == "1"
            es_jurisdiccional = row.get("es_distrito_judicial") == "1"
            estatus = row.get("estatus")
            Distrito(
                clave=clave,
                nombre=nombre,
                nombre_corto=nombre_corto,
                es_activo=es_activo,
                es_distrito_judicial=es_distrito_judicial,
                es_distrito=es_distrito,
                es_jurisdiccional=es_jurisdiccional,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} distritos alimentados.", fg="green"))
