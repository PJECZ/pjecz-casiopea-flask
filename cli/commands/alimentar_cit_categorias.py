"""
Alimentar Cit Categorías
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

import click
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pjecz_casiopea_flask.blueprints.cit_categorias.models import CitCategoria
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string

CIT_SERVICIOS_CSV = "seed/cit_servicios.csv"


def alimentar_cit_categorias():
    """Alimentar Cit Categorías"""
    ruta = Path(CIT_SERVICIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando cit_servicios: ", nl=False)
    cit_categorias_claves = []
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            cit_categoria_clave = safe_clave(row.get("cit_categoria_clave"))
            cit_categoria_nombre = safe_string(row.get("cit_categoria_nombre"), save_enie=True)
            cit_categoria_es_activo = row.get("cit_categoria_es_activo") == "1"
            if cit_categoria_clave not in cit_categorias_claves:
                cit_categoria = CitCategoria(
                    clave=cit_categoria_clave,
                    nombre=cit_categoria_nombre,
                    es_activo=cit_categoria_es_activo,
                )
                cit_categoria.save()
                cit_categorias_claves.append(cit_categoria_clave)
                contador += 1
                click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} cit_categorias alimentadas.", fg="green"))
