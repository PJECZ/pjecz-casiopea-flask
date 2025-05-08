"""
Alimentar Cit Servicios
"""

import csv
from datetime import datetime
from pathlib import Path
import sys

import click
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from pjecz_casiopea_flask.blueprints.cit_categorias.models import CitCategoria
from pjecz_casiopea_flask.blueprints.cit_servicios.models import CitServicio
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string

CIT_SERVICIOS_CSV = "seed/cit_servicios.csv"


def alimentar_cit_servicios():
    """Alimentar Cit Servicios"""
    ruta = Path(CIT_SERVICIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando cit_servicios: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            cit_categoria_clave = safe_clave(row["cit_categoria_clave"])
            cit_categoria_nombre = safe_string(row["cit_categoria_nombre"], save_enie=True)
            cit_categoria = None
            try:
                cit_categoria = CitCategoria.query.filter(CitCategoria.clave == cit_categoria_clave).one()
            except (MultipleResultsFound, NoResultFound):
                cit_categoria = CitCategoria(
                    clave=cit_categoria_clave,
                    nombre=cit_categoria_nombre,
                )
                cit_categoria.save()
            clave = safe_clave(row["clave"])
            descripcion = safe_string(row["descripcion"], save_enie=True)
            duracion = datetime.strptime(row["duracion"], "%H:%M").time()
            documentos_limite = int(row["documentos_limite"])
            desde = datetime.strptime(row["desde"], "%H:%M").time()
            hasta = datetime.strptime(row["hasta"], "%H:%M").time()
            dias_habilitados = row["dias_habilitados"]
            estatus = row["estatus"]
            CitServicio(
                cit_categoria_id=cit_categoria.id,
                clave=clave,
                descripcion=descripcion,
                duracion=duracion,
                documentos_limite=documentos_limite,
                desde=desde,
                hasta=hasta,
                dias_habilitados=dias_habilitados,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} cit_servicios alimentados.", fg="green"))
