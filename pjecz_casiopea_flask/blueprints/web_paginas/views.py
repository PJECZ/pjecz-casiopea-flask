"""
Web Páginas, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_path, safe_string
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..web_ramas.models import WebRama
from .forms import (
    WebPaginaEditCKEditor5Form,
    WebPaginaEditForm,
    WebPaginaEditSyncfusionDocumentEditorForm,
    WebPaginaEditSyncfusionMarkdownEditorForm,
    WebPaginaNewForm,
)
from .models import WebPagina

MODULO = "WEB PAGINAS"

web_paginas = Blueprint("web_paginas", __name__, template_folder="templates")


@web_paginas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@web_paginas.route("/web_paginas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Web Paginas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = WebPagina.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(WebPagina.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(WebPagina.estatus == "A")
    if "web_rama_id" in request.form:
        consulta = consulta.filter(WebPagina.web_rama_id == request.form["web_rama_id"])
    if "clave" in request.form:
        clave = safe_clave(request.form["clave"])
        if clave != "":
            consulta = consulta.filter(WebPagina.clave.contains(clave))
    if "descripcion" in request.form:
        descripcion = safe_string(request.form["descripcion"], save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(WebPagina.descripcion.contains(descripcion))
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    if "esta_archivado" in request.form:
        consulta = consulta.filter(WebPagina.esta_archivado == bool(request.form["esta_archivado"]))
    # Ordenar y paginar
    registros = consulta.order_by(WebPagina.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("web_paginas.detail", web_pagina_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
                "titulo": resultado.titulo,
                "estado": resultado.estado,
                "tiempo_publicar": resultado.tiempo_publicar.strftime("%Y-%m-%d %H:%M") if resultado.tiempo_publicar else "",
                "tiempo_archivar": resultado.tiempo_archivar.strftime("%Y-%m-%d %H:%M") if resultado.tiempo_archivar else "",
                "web_rama_clave": resultado.web_rama.clave,
                "esta_archivado": resultado.esta_archivado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@web_paginas.route("/web_paginas")
def list_active():
    """Listado de Web Páginas activos"""
    return render_template(
        "web_paginas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Páginas",
        estatus="A",
    )


@web_paginas.route("/web_paginas/inactivos")
def list_inactive():
    """Listado de Web Páginas inactivos"""
    return render_template(
        "web_paginas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Páginas inactivos",
        estatus="B",
    )


@web_paginas.route("/web_paginas/<web_pagina_id>")
def detail(web_pagina_id):
    """Detalle de un Web Página"""
    web_pagina = WebPagina.query.get_or_404(web_pagina_id)
    return render_template("web_paginas/detail.jinja2", web_pagina=web_pagina)


@web_paginas.route("/web_paginas/nuevo/<web_rama_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(web_rama_id):
    """Nuevo Web Página"""
    web_rama = WebRama.query.get_or_404(web_rama_id)
    form = WebPaginaNewForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que la clave no se repita
        clave = safe_clave(form.clave.data)
        if WebPagina.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
            es_valido = False
        # Si es válido, guardar
        if es_valido is True:
            web_pagina = WebPagina(
                web_rama_id=web_rama.id,
                clave=clave,
                descripcion=safe_string(form.descripcion.data, save_enie=True),
                titulo=safe_string(form.titulo.data, do_unidecode=False, save_enie=True, to_uppercase=False),
                ruta=safe_path(form.ruta.data),
            )
            web_pagina.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Web Página {web_pagina.clave}"),
                url=url_for("web_paginas.detail", web_pagina_id=web_pagina.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = web_rama.clave
    form.ruta.data = f"{web_rama.directorio}/"
    return render_template("web_paginas/new.jinja2", form=form, web_rama=web_rama)


@web_paginas.route("/web_paginas/edicion/<web_pagina_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(web_pagina_id):
    """Editar Web Página"""
    web_pagina = WebPagina.query.get_or_404(web_pagina_id)
    form = WebPaginaEditForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no está en uso
        clave = safe_clave(form.clave.data)
        if web_pagina.clave != clave:
            web_pagina_existente = WebPagina.query.filter_by(clave=clave).first()
            if web_pagina_existente and web_pagina_existente.id != web_pagina.id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si es válido, actualizar
        if es_valido:
            web_pagina.clave = clave
            web_pagina.descripcion = safe_string(form.descripcion.data, save_enie=True)
            web_pagina.titulo = safe_string(form.titulo.data, do_unidecode=False, save_enie=True, to_uppercase=False)
            web_pagina.ruta = safe_path(form.ruta.data)
            web_pagina.fecha_modificacion = form.fecha_modificacion.data
            web_pagina.responsable = safe_string(form.responsable.data, save_enie=True, to_uppercase=False)
            web_pagina.etiquetas = safe_string(form.etiquetas.data, save_enie=True, to_uppercase=False)
            web_pagina.vista_previa = form.vista_previa.data.strip()
            web_pagina.tiempo_publicar = form.tiempo_publicar.data
            web_pagina.tiempo_archivar = form.tiempo_archivar.data
            web_pagina.esta_archivado = form.esta_archivado.data
            web_pagina.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Web Página {web_pagina.clave}"),
                url=url_for("web_paginas.detail", web_pagina_id=web_pagina.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = web_pagina.clave
    form.descripcion.data = web_pagina.descripcion
    form.titulo.data = web_pagina.titulo
    form.ruta.data = web_pagina.ruta
    form.fecha_modificacion.data = web_pagina.fecha_modificacion
    form.responsable.data = web_pagina.responsable
    form.etiquetas.data = web_pagina.etiquetas
    form.vista_previa.data = web_pagina.vista_previa
    form.tiempo_publicar.data = web_pagina.tiempo_publicar
    form.tiempo_archivar.data = web_pagina.tiempo_archivar
    form.esta_archivado.data = web_pagina.esta_archivado
    return render_template("web_paginas/edit.jinja2", form=form, web_pagina=web_pagina)


@web_paginas.route("/web_paginas/edicion_ckeditor5/<web_pagina_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_ckeditor5(web_pagina_id):
    """Editar contenido de Web Página con CKEditor5"""
    web_pagina = WebPagina.query.get_or_404(web_pagina_id)
    form = WebPaginaEditCKEditor5Form()
    if form.validate_on_submit():
        web_pagina.contenido_html = form.contenido_html.data.strip()
        web_pagina.contenido_md = form.contenido_md.data.strip()
        web_pagina.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado contenido de Web Página {web_pagina.clave} con CKEditor5"),
            url=url_for("web_paginas.detail", web_pagina_id=web_pagina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.contenido_html.data = web_pagina.contenido_html
    form.contenido_md.data = web_pagina.contenido_md
    return render_template("web_paginas/edit_ckeditor5.jinja2", form=form, web_pagina=web_pagina)


@web_paginas.route("/web_paginas/edicion_syncfusion_document/<web_pagina_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_syncfusion_document(web_pagina_id):
    """Editar contenido de Web Página con Syncfusion Document Editor"""
    web_pagina = WebPagina.query.get_or_404(web_pagina_id)
    form = WebPaginaEditSyncfusionDocumentEditorForm()
    if form.validate_on_submit():
        web_pagina.contenido_sfdt = form.contenido_sfdt.data.strip()
        web_pagina.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado contenido de Web Página {web_pagina.clave} con Syncfusion Document Editor"),
            url=url_for("web_paginas.detail", web_pagina_id=web_pagina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.contenido_sfdt.data = web_pagina.contenido_sfdt
    return render_template("web_paginas/edit_syncfusion_document.jinja2", form=form, web_pagina=web_pagina)


@web_paginas.route("/web_paginas/edicion_syncfusion_markdown/<web_pagina_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_syncfusion_markdown(web_pagina_id):
    """Editar contenido de Web Página con Syncfusion Markdown Editor"""
    web_pagina = WebPagina.query.get_or_404(web_pagina_id)
    form = WebPaginaEditSyncfusionMarkdownEditorForm()
    if form.validate_on_submit():
        web_pagina.contenido_html = form.contenido_html.data.strip()
        web_pagina.contenido_md = form.contenido_md.data.strip()
        web_pagina.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado contenido de Web Página {web_pagina.clave} con Syncfusion Markdown Editor"),
            url=url_for("web_paginas.detail", web_pagina_id=web_pagina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.contenido_html.data = web_pagina.contenido_html
    form.contenido_md.data = web_pagina.contenido_md
    return render_template("web_paginas/edit_syncfusion_markdown.jinja2", form=form, web_pagina=web_pagina)


@web_paginas.route("/web_paginas/eliminar/<web_pagina_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(web_pagina_id):
    """Eliminar Web Página"""
    web_pagina = WebPagina.query.get_or_404(web_pagina_id)
    if web_pagina.estatus == "A":
        web_pagina.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Web Página {web_pagina.clave}"),
            url=url_for("web_paginas.detail", web_pagina_id=web_pagina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("web_paginas.detail", web_pagina_id=web_pagina.id))


@web_paginas.route("/web_paginas/recuperar/<web_pagina_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(web_pagina_id):
    """Recuperar Web Página"""
    web_pagina = WebPagina.query.get_or_404(web_pagina_id)
    if web_pagina.estatus == "B":
        web_pagina.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Web Página {web_pagina.clave}"),
            url=url_for("web_paginas.detail", web_pagina_id=web_pagina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("web_paginas.detail", web_pagina_id=web_pagina.id))
