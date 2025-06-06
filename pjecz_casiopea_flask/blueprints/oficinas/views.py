"""
Oficinas, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..oficinas.forms import OficinaForm
from ..oficinas.models import Oficina
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_string

MODULO = "OFICINAS"

oficinas = Blueprint("oficinas", __name__, template_folder="templates")


@oficinas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@oficinas.route("/oficinas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Oficinas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Oficina.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(Oficina.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(Oficina.estatus == "A")
    if "domicilio_id" in request.form:
        consulta = consulta.filter(Oficina.domicilio_id == request.form["domicilio_id"])
    if "clave" in request.form:
        try:
            clave = safe_clave(request.form["clave"])
            if clave != "":
                consulta = consulta.filter(Oficina.clave.contains(clave))
        except ValueError:
            pass
    if "descripcion_corta" in request.form:
        descripcion_corta = safe_string(request.form["descripcion_corta"], save_enie=True)
        if descripcion_corta != "":
            consulta = consulta.filter(Oficina.descripcion_corta.contains(descripcion_corta))
    # Ordenar y paginar
    registros = consulta.order_by(Oficina.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("oficinas.detail", oficina_id=resultado.id),
                },
                "descripcion_corta": resultado.descripcion_corta,
                "domicilio_edificio": resultado.domicilio.edificio,
                "apertura": resultado.apertura.strftime("%H:%M"),
                "cierre": resultado.cierre.strftime("%H:%M"),
                "limite_personas": resultado.limite_personas,
                "es_jurisdiccional": resultado.es_jurisdiccional,
                "puede_agendar_citas": resultado.puede_agendar_citas,
                "puede_enviar_qr": resultado.puede_enviar_qr,
                "es_activo": resultado.es_activo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@oficinas.route("/oficinas")
def list_active():
    """Listado de Oficina activas"""
    return render_template(
        "oficinas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Oficinas",
        estatus="A",
    )


@oficinas.route("/oficinas/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Oficinas inactivas"""
    return render_template(
        "oficinas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Oficinas inactivos",
        estatus="B",
    )


@oficinas.route("/oficinas/<oficina_id>")
def detail(oficina_id):
    """Detalle de una Oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    return render_template("oficinas/detail.jinja2", oficina=oficina)


@oficinas.route("/oficinas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Oficina"""
    form = OficinaForm()
    if form.validate_on_submit():
        # Validar que la clave no se repita
        clave = safe_clave(form.clave.data, max_len=32)
        if Oficina.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
            return render_template("oficinas/new.jinja2", form=form)
        # Guardar
        oficina = Oficina(
            clave=clave,
            descripcion=safe_string(form.descripcion.data, max_len=512, save_enie=True),
            descripcion_corta=safe_string(form.descripcion_corta.data, max_len=64, save_enie=True),
            domicilio_id=form.domicilio.data,
            apertura=form.apertura.data,
            cierre=form.cierre.data,
            limite_personas=form.limite_personas.data,
            es_jurisdiccional=form.es_jurisdiccional.data,
            puede_agendar_citas=form.puede_agendar_citas.data,
            puede_enviar_qr=form.puede_enviar_qr.data,
            es_activo=form.es_activo.data,
        )
        oficina.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Oficina {oficina.clave}"),
            url=url_for("oficinas.detail", oficina_id=oficina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("oficinas/new.jinja2", form=form)


@oficinas.route("/oficinas/edicion/<oficina_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(oficina_id):
    """Editar Oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    form = OficinaForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no este en uso
        clave = safe_clave(form.clave.data, max_len=32)
        if oficina.clave != clave:
            oficina_existente = Oficina.query.filter_by(clave=clave).first()
            if oficina_existente and oficina_existente.id != oficina_id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si es valido actualizar
        if es_valido:
            oficina.clave = clave
            oficina.descripcion = safe_string(form.descripcion.data, max_len=512, save_enie=True)
            oficina.descripcion_corta = safe_string(form.descripcion_corta.data, max_len=64, save_enie=True)
            oficina.domicilio_id = form.domicilio.data
            oficina.apertura = form.apertura.data
            oficina.cierre = form.cierre.data
            oficina.limite_personas = form.limite_personas.data
            oficina.es_jurisdiccional = form.es_jurisdiccional.data
            oficina.puede_agendar_citas = form.puede_agendar_citas.data
            oficina.puede_enviar_qr = form.puede_enviar_qr.data
            oficina.es_activo = form.es_activo.data
            oficina.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Oficina {oficina.clave}"),
                url=url_for("oficinas.detail", oficina_id=oficina.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = oficina.clave
    form.descripcion_corta.data = oficina.descripcion_corta
    form.descripcion.data = oficina.descripcion
    form.domicilio.data = oficina.domicilio_id  # Se manda domicilio_id porque es un select
    form.apertura.data = oficina.apertura
    form.cierre.data = oficina.cierre
    form.limite_personas.data = oficina.limite_personas
    form.es_jurisdiccional.data = oficina.es_jurisdiccional
    form.puede_agendar_citas.data = oficina.puede_agendar_citas
    form.puede_enviar_qr.data = oficina.puede_enviar_qr
    form.es_activo.data = oficina.es_activo
    return render_template("oficinas/edit.jinja2", form=form, oficina=oficina)


@oficinas.route("/oficinas/eliminar/<oficina_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(oficina_id):
    """Eliminar Oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    if oficina.estatus == "A":
        oficina.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Oficina {oficina.clave}"),
            url=url_for("oficinas.detail", oficina_id=oficina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("oficinas.detail", oficina_id=oficina.id))


@oficinas.route("/oficinas/recuperar/<oficina_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(oficina_id):
    """Recuperar Oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    if oficina.estatus == "B":
        oficina.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Oficina {oficina.clave}"),
            url=url_for("oficinas.detail", oficina_id=oficina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("oficinas.detail", oficina_id=oficina.id))


@oficinas.route("/oficinas/select_json", methods=["POST"])
def query_oficinas_json():
    """Proporcionar el JSON de oficinas para elegir con un Select2"""
    consulta = Oficina.query.filter(Oficina.estatus == "A")
    if "searchString" in request.form:
        clave_o_descripcion_corta = safe_string(request.form["searchString"], save_enie=True)
        if clave_o_descripcion_corta != "":
            consulta = consulta.filter(
                or_(
                    Oficina.clave.contains(clave_o_descripcion_corta),
                    Oficina.descripcion_corta.contains(clave_o_descripcion_corta),
                ),
            )
    resultados = []
    for oficina in consulta.order_by(Oficina.clave).limit(20).all():
        resultados.append({"id": oficina.id, "text": f"{oficina.clave} - {oficina.descripcion_corta}"})
    return {"results": resultados, "pagination": {"more": False}}
