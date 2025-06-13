"""
Alimentar Cit Servicios
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

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
        cit_categoria_clave = None
        rows = csv.DictReader(puntero)
        for row in rows:
            if cit_categoria_clave is None or cit_categoria_clave != row.get("cit_categoria_clave"):
                cit_categoria_clave = row.get("cit_categoria_clave")
                cit_categoria = CitCategoria.query.filter(CitCategoria.clave == cit_categoria_clave).one()
            clave = safe_clave(row.get("clave"))
            descripcion = safe_string(row.get("descripcion"), save_enie=True)
            duracion = datetime.strptime(row.get("duracion"), "%H:%M").time()
            documentos_limite = int(row.get("documentos_limite"))
            desde = datetime.strptime(row.get("desde"), "%H:%M").time()
            hasta = datetime.strptime(row.get("hasta"), "%H:%M").time()
            dias_habilitados = row.get("dias_habilitados")
            es_activo = row.get("es_activo") == "1"
            estatus = row.get("estatus")
            CitServicio(
                cit_categoria_id=cit_categoria.id,
                clave=clave,
                descripcion=descripcion,
                duracion=duracion,
                documentos_limite=documentos_limite,
                desde=desde,
                hasta=hasta,
                dias_habilitados=dias_habilitados,
                es_activo=es_activo,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} cit_servicios alimentados.", fg="green"))
