"""
Alimentar Autoridades
"""

import csv
import sys
from pathlib import Path

import click

from pjecz_casiopea_flask.blueprints.materias.models import Materia
from pjecz_casiopea_flask.blueprints.autoridades.models import Autoridad
from pjecz_casiopea_flask.blueprints.distritos.models import Distrito
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string

AUTORIDADES_CSV = "seed/autoridades.csv"


def alimentar_autoridades():
    """Alimentar Autoridades"""
    ruta = Path(AUTORIDADES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando autoridades: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            distrito_clave = safe_clave(row.get("distrito_clave"))
            materia_clave = safe_clave(row.get("materia_clave"))
            clave = safe_clave(row.get("clave"))
            descripcion = safe_string(row.get("descripcion"), save_enie=True)
            descripcion_corta = safe_string(row.get("descripcion_corta"), save_enie=True)
            es_jurisdiccional = row.get("es_jurisdiccional") == "1"
            estatus = row.get("estatus")
            distrito = Distrito.query.filter(Distrito.clave == distrito_clave).first()
            if distrito is None:
                click.echo(click.style(f"  AVISO: distrito {distrito_clave} no existe", fg="red"))
                sys.exit(1)
            materia = Materia.query.filter(Materia.clave == materia_clave).first()
            if materia is None:
                click.echo(click.style(f"  AVISO: materia {materia_clave} no existe", fg="red"))
                sys.exit(1)
            Autoridad(
                distrito=distrito,
                materia=materia,
                clave=clave,
                descripcion=descripcion,
                descripcion_corta=descripcion_corta,
                es_jurisdiccional=es_jurisdiccional,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} autoridades alimentadas.", fg="green"))
