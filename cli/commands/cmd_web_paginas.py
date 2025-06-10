"""
CLI Web Páginas
"""

import re
import sys
from datetime import datetime
from pathlib import Path

import click
from markdown import markdown
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from pjecz_casiopea_flask.blueprints.web_paginas.models import WebPagina
from pjecz_casiopea_flask.blueprints.web_ramas.models import WebRama
from pjecz_casiopea_flask.config.extensions import database, pwd_context
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string
from pjecz_casiopea_flask.main import app

METADATO_REGEXP = r"^(\w+)\s*:\s*(.+)$"
UNIDADES_COMPARTIDAS_DIR = "/var/mnt/demeter/Sitios Web/pjecz.gob.mx"

app.app_context().push()
database.app = app


@click.group()
def cli():
    """Cit Clientes"""


@click.command()
def alimentar_noticias():
    """Agregar páginas de la rama Noticias"""

    # Validar el directorio
    noticias_path = Path(f"{UNIDADES_COMPARTIDAS_DIR}/Noticias")
    if not noticias_path.exists():
        click.echo("AVISO: NO existe el directorio de Noticias.")
        sys.exit(1)
    if not noticias_path.is_dir():
        click.echo("AVISO: NO es un directorio. No puedo buscar Noticias.")
        sys.exit(1)

    # Consultar la rama Noticias
    try:
        web_rama = WebRama.query.filter_by(clave="NT").one()
    except (MultipleResultsFound, NoResultFound):
        click.echo("AVISO: No se encontró la rama Noticias")
        sys.exit(1)

    # Bucle por los archivos MD
    contador = 0
    archivos_md = list(Path(noticias_path).rglob("*.md"))
    click.echo("Leyendo los archivos MD con Noticias: ", nl=False)
    for archivo_md in archivos_md:
        # Inicializar el listado con las líneas sin metadatos
        contenido = []
        # Inicializar el diccionario para los metadatos
        metadatos = {}
        # Leer el contenido del archivo MD
        with open(file=archivo_md, mode="r", encoding="UTF8") as archivo:
            # Suponemos que los metadatos solo están al principio del archivo
            es_metadatato = True
            # Bucle por cada línea del archivo
            for linea in archivo.read().split("\n"):
                if es_metadatato is False:
                    contenido.append(linea)
                elif patron := re.match(METADATO_REGEXP, linea):
                    etiqueta = patron.group(1).strip().capitalize()
                    valor = patron.group(2).strip()
                    metadatos[etiqueta] = valor
                else:
                    es_metadatato = False
        # Validar contenido
        if len(contenido) == 0:
            click.echo(click.style("[c]", fg="yellow"), nl=False)
            continue  # Se omite esta página porque no tiene contenido
        # Validar clave
        clave = metadatos.get("Key")
        if not clave:
            click.echo(click.style("[k]", fg="yellow"), nl=False)
            continue  # Se omite esta página porque no tiene clave
        if WebPagina.query.filter_by(clave=clave).first():
            click.echo(click.style("[.]", fg="blue"), nl=False)
            continue  # Se omite esta página porque ya está en la base de datos
        # Validar título
        titulo = "Sin título"
        if metadatos.get("Title"):
            titulo = safe_string(metadatos["Title"], do_unidecode=True, save_enie=True, to_uppercase=False)
        # Validar descripción
        descripcion = "Sin descripción"
        if metadatos.get("Summary"):
            descripcion = safe_string(metadatos["Summary"], save_enie=True)
        # Validar la fecha de modificación
        fecha_modificacion = datetime(year=2000, month=1, day=1).date()
        if metadatos.get("Date"):
            try:
                fecha_modificacion = datetime.strptime(metadatos["Date"], "%Y-%m-%d").date()
            except ValueError:
                pass
        # Validar estado
        estado = "PUBLICADO"
        if metadatos.get("Status") and metadatos["Status"].upper() == "DRAFT":
            estado = "BORRADOR"
        if metadatos.get("Status") and metadatos["Status"].upper() == "HIDDEN":
            estado = "BORRADOR"
        # Insertar
        WebPagina(
            web_rama_id=web_rama.id,
            clave=clave,
            descripcion=descripcion,
            titulo=titulo,
            ruta="",
            fecha_modificacion=fecha_modificacion,
            estado=estado,
            contenido_md="\n".join(contenido),
            contenido_html=markdown("\n".join(contenido), extensions=["tables"]),
        ).save()
        # Mostrar el Key en verde si lo tiene, de lo contrario corchetes amarillos
        if metadatos.get("Key"):
            click.echo(click.style(f"[{metadatos['Key']}]", fg="green"), nl=False)
        else:
            click.echo(click.style("[]", fg="yellow"), nl=False)
        # Incrementar el contador
        contador += 1

    # Mensaje final
    click.echo()
    click.echo(click.style(f"  {contador} noticias alimentadas.", fg="green"))


cli.add_command(alimentar_noticias)
