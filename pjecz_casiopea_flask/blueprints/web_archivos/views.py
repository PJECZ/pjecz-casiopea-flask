"""
Web Archivos, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_string, safe_url
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..web_paginas.models import WebPagina
from .forms import WebArchivoEditForm, WebArchivoNewForm
from .models import WebArchivo

MODULO = "WEB ARCHIVOS"

web_archivos = Blueprint("web_archivos", __name__, template_folder="templates")


@web_archivos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@web_archivos.route("/web_archivos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Web Archivos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = WebArchivo.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(WebArchivo.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(WebArchivo.estatus == "A")
    if "web_pagina_id" in request.form:
        consulta = consulta.filter_by(web_pagina_id=request.form["web_pagina_id"])
    if "clave" in request.form:
        clave = safe_clave(request.form["clave"])
        if clave != "":
            consulta = consulta.filter(WebArchivo.clave.contains(clave))
    if "descripcion" in request.form:
        descripcion = safe_string(request.form["nombre"], save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(WebArchivo.nombre.contains(descripcion))
    if "esta_archivado" in request.form:
        consulta = consulta.filter(WebArchivo.esta_archivado == bool(request.form["esta_archivado"]))
    # Ordenar y paginar
    registros = consulta.order_by(WebArchivo.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("web_archivos.detail", web_archivo_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "ruta": resultado.ruta,
                "archivo": resultado.archivo,
                "descripcion": resultado.descripcion,
                "web_pagina_clave": resultado.web_pagina.clave,
                "archivado": resultado.esta_archivado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@web_archivos.route("/web_archivos")
def list_active():
    """Listado de Web Archivos activos"""
    return render_template(
        "web_archivos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Archivos",
        estatus="A",
    )


@web_archivos.route("/web_archivos/inactivos")
def list_inactive():
    """Listado de Web Archivos inactivos"""
    return render_template(
        "web_archivos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Archivos inactivos",
        estatus="B",
    )


@web_archivos.route("/web_archivos/<web_archivo_id>")
def detail(web_archivo_id):
    """Detalle de un Web Archivo"""
    web_archivo = WebArchivo.query.get_or_404(web_archivo_id)
    return render_template("web_archivos/detail.jinja2", web_archivo=web_archivo)


@web_archivos.route("/web_archivos/nuevo/<web_pagina_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(web_pagina_id):
    """Nuevo Web Archivo"""
    web_pagina = WebPagina.query.get_or_404(web_pagina_id)
    form = WebArchivoNewForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que la clave no se repita
        clave = safe_clave(form.clave.data)
        if WebArchivo.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
            es_valido = False
        # Tomar valores del formulario
        nombre = safe_string(form.nombre.data, save_enie=True)
        titulo = safe_string(form.titulo.data, do_unidecode=False, save_enie=True, to_uppercase=False)
        archivo = form.archivo.data.strip()
        url = safe_url(form.url.data)
        # Si es válido, guardar
        if es_valido is True:
            web_archivo = WebArchivo(
                web_pagina_id=web_pagina.id,
                clave=clave,
                nombre=nombre,
                titulo=titulo,
                archivo=archivo,
                url=url,
            )
            web_archivo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Web Archivo {web_archivo.clave}"),
                url=url_for("web_archivos.detail", web_archivo_id=web_archivo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = web_pagina.clave
    return render_template("web_archivos/new.jinja2", form=form)


@web_archivos.route("/web_archivos/edicion/<web_archivo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(web_archivo_id):
    """Editar Web Archivo"""
    web_archivo = WebArchivo.query.get_or_404(web_archivo_id)
    form = WebArchivoEditForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no está en uso
        clave = safe_clave(form.clave.data)
        if web_archivo.clave != clave:
            web_archivo_existente = WebArchivo.query.filter_by(clave=clave).first()
            if web_archivo_existente and web_archivo_existente.id != web_archivo.id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si es válido, actualizar
        if es_valido:
            web_archivo.clave = clave
            web_archivo.nombre = safe_string(form.nombre.data, save_enie=True)
            web_archivo.titulo = safe_string(form.titulo.data, do_unidecode=False, save_enie=True, to_uppercase=False)
            web_archivo.archivo = form.archivo.data.strip()
            web_archivo.url = safe_url(form.url.data)
            web_archivo.esta_archivado = form.esta_archivado.data
            web_archivo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Web Archivo {web_archivo.clave}"),
                url=url_for("web_archivos.detail", web_archivo_id=web_archivo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = web_archivo.clave
    form.nombre.data = web_archivo.nombre
    form.titulo.data = web_archivo.titulo
    form.archivo.data = web_archivo.archivo
    form.url.data = web_archivo.url
    form.esta_archivado.data = web_archivo.esta_archivado
    return render_template("web_archivos/edit.jinja2", form=form, web_archivo=web_archivo)


@web_archivos.route("/web_archivos/eliminar/<web_archivo_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(web_archivo_id):
    """Eliminar Web Archivo"""
    web_archivo = WebArchivo.query.get_or_404(web_archivo_id)
    if web_archivo.estatus == "A":
        web_archivo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Web Archivo {web_archivo.clave}"),
            url=url_for("web_archivos.detail", web_archivo_id=web_archivo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("web_archivos.detail", web_archivo_id=web_archivo.id))


@web_archivos.route("/web_archivos/recuperar/<web_archivo_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(web_archivo_id):
    """Recuperar Web Archivo"""
    web_archivo = WebArchivo.query.get_or_404(web_archivo_id)
    if web_archivo.estatus == "B":
        web_archivo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Web Archivo {web_archivo.clave}"),
            url=url_for("web_archivos.detail", web_archivo_id=web_archivo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("web_archivos.detail", web_archivo_id=web_archivo.id))
