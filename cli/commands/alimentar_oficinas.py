"""
Alimentar Oficinas
"""

import csv
from datetime import datetime
from pathlib import Path
import sys

import click
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from pjecz_casiopea_flask.blueprints.domicilios.models import Domicilio
from pjecz_casiopea_flask.blueprints.oficinas.models import Oficina
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string

OFICINAS_CSV = "seed/oficinas.csv"


def alimentar_oficinas():
    """Alimentar Oficinas"""
    ruta = Path(OFICINAS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando oficinas: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            edificio = safe_string(row["edificio"], save_enie=True)
            clave = safe_clave(row["clave"])
            descripcion = safe_string(row["descripcion"], save_enie=True)
            descripcion_corta = safe_string(row["descripcion_corta"], save_enie=True)
            es_jurisdiccional = row["es_jurisdiccional"] == "1"
            puede_agendar_citas = row["puede_agendar_citas"] == "1"
            apertura = datetime.strptime(row["apertura"], "%H:%M").time()
            cierre = datetime.strptime(row["cierre"], "%H:%M").time()
            limite_personas = int(row["limite_personas"])
            puede_enviar_qr = row["puede_enviar_qr"] == "1"
            estatus = row["estatus"]
            try:
                domicilio = Domicilio.query.filter(Domicilio.edificio == edificio).one()
            except (MultipleResultsFound, NoResultFound):
                click.echo(f"AVISO: Edificio {edificio} no existe.")
                sys.exit(1)
            Oficina(
                domicilio=domicilio,
                clave=clave,
                descripcion=descripcion,
                descripcion_corta=descripcion_corta,
                es_jurisdiccional=es_jurisdiccional,
                puede_agendar_citas=puede_agendar_citas,
                apertura=apertura,
                cierre=cierre,
                limite_personas=limite_personas,
                puede_enviar_qr=puede_enviar_qr,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} oficinas alimentadas.", fg="green"))
