"""
Alimentar Domicilios
"""

import csv
import sys
from pathlib import Path

import click

from pjecz_casiopea_flask.blueprints.domicilios.models import Domicilio
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string

DOMICILIOS_CSV = "seed/domicilios.csv"


def alimentar_domicilios():
    """Alimentar Domicilios"""
    ruta = Path(DOMICILIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando domicilios: ", nl=False)
    contador = 0
    with (open(ruta, encoding="utf8") as puntero):
        rows = csv.DictReader(puntero)
        for row in rows:
            edificio = safe_string(row["edificio"], save_enie=True)
            estado = safe_string(row["estado"], save_enie=True)
            municipio = safe_string(row["municipio"], save_enie=True)
            calle = safe_string(row["calle"], save_enie=True)
            num_ext = safe_string(row["num_ext"])
            num_int = safe_string(row["num_int"])
            colonia = safe_string(row["colonia"], save_enie=True)
            cp = int(row["cp"])
            estatus = row["estatus"]
            domicilio = Domicilio(
                edificio=edificio,
                estado=estado,
                municipio=municipio,
                calle=calle,
                num_ext=num_ext,
                num_int=num_int,
                colonia=colonia,
                cp=cp,
                completo=f"",
                estatus=estatus,
            )
            domicilio.completo = domicilio.elaborar_completo()
            domicilio.save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} domicilios alimentados.", fg="green"))
