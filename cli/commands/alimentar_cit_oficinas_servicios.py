"""
Alimentar Cit Oficinas Servicios
"""

import csv
from datetime import datetime
from pathlib import Path
import sys

import click
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from pjecz_casiopea_flask.blueprints.cit_oficinas_servicios.models import CitOficinaServicio
from pjecz_casiopea_flask.blueprints.cit_servicios.models import CitServicio
from pjecz_casiopea_flask.blueprints.oficinas.models import Oficina
from pjecz_casiopea_flask.lib.safe_string import safe_clave

CIT_SERVICIOS_CSV = "seed/cit_oficinas_servicios.csv"


def alimentar_cit_oficinas_servicios():
    """Alimentar Cit Oficinas Servicios"""
    ruta = Path(CIT_SERVICIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando cit_oficinas_servicios: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            cit_servicio_clave = safe_clave(row.get("cit_servicio_clave"))
            try:
                cit_servicio = CitServicio.query.filter(CitServicio.clave == cit_servicio_clave).one()
            except (MultipleResultsFound, NoResultFound):
                click.echo(click.style(f"  AVISO: servicio {cit_servicio_clave} no existe", fg="red"))
                sys.exit(1)
            oficina_clave = safe_clave(row.get("oficina_clave"))
            try:
                oficina = Oficina.query.filter(Oficina.clave == oficina_clave).one()
            except (MultipleResultsFound, NoResultFound):
                click.echo(click.style(f"  AVISO: oficina {oficina_clave} no existe", fg="red"))
                sys.exit(1)
            CitOficinaServicio(
                cit_servicio_id=cit_servicio.id,
                oficina_id=oficina.id,
                descripcion=f"Oficina {oficina_clave} tiene el servicio {cit_servicio_clave}",
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} cit_oficinas_servicios alimentados.", fg="green"))
