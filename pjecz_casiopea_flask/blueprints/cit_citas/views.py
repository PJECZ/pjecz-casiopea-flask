"""
Cit Citas, vistas
"""

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..cit_clientes.models import CitCliente
from ..cit_servicios.models import CitServicio
from ..modulos.models import Modulo
from ..oficinas.models import Oficina
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .models import CitCita

MODULO = "CIT CITAS"

cit_citas = Blueprint("cit_citas", __name__, template_folder="templates")


@cit_citas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_citas.route("/cit_citas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Cit Citas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CitCita.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(CitCita.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(CitCita.estatus == "A")
    if "id" in request.form:
        consulta = consulta.filter(CitCita.id == request.form["id"])
    if "cit_cliente_id" in request.form:
        consulta = consulta.filter(CitCita.cit_cliente_id == request.form["cit_cliente_id"])
    if "cit_servicio_id" in request.form:
        consulta = consulta.filter(CitCita.cit_servicio_id == request.form["cit_servicio_id"])
    if "oficina_id" in request.form:
        consulta = consulta.filter(CitCita.oficina_id == request.form["oficina_id"])
    if "estado" in request.form:
        estado = safe_string(request.form["estado"])
        if estado != "":
            consulta = consulta.filter(CitCita.estado == estado)
    # Luego filtrar por columnas de otras tablas
    cit_cliente_email = ""
    if "cit_cliente_email" in request.form:
        cit_cliente_email = safe_email(request.form["cit_cliente_email"], search_fragment=True)
    cit_cliente_nombres = ""
    if "cit_cliente_nombres" in request.form:
        cit_cliente_nombres = safe_string(request.form["cit_cliente_nombres"], save_enie=True)
    cit_cliente_apellido_primero = ""
    if "cit_cliente_apellido_primero" in request.form:
        cit_cliente_apellido_primero = safe_string(request.form["cit_cliente_apellido_primero"], save_enie=True)
    cit_cliente_apellido_segundo = ""
    if "cit_cliente_apellido_segundo" in request.form:
        cit_cliente_apellido_segundo = safe_string(request.form["cit_cliente_apellido_segundo"], save_enie=True)
    if (
        cit_cliente_email != ""
        or cit_cliente_nombres != ""
        or cit_cliente_apellido_primero != ""
        or cit_cliente_apellido_segundo != ""
    ):
        consulta = consulta.join(CitCliente)
        if cit_cliente_email != "":
            consulta = consulta.filter(CitCliente.email.contains(cit_cliente_email))
        if cit_cliente_nombres != "":
            consulta = consulta.filter(CitCliente.nombres.contains(cit_cliente_nombres))
        if cit_cliente_apellido_primero != "":
            consulta = consulta.filter(CitCliente.apellido_primero.contains(cit_cliente_apellido_primero))
        if cit_cliente_apellido_segundo != "":
            consulta = consulta.filter(CitCliente.apellido_segundo.contains(cit_cliente_apellido_segundo))
    # Ordenar y paginar
    registros = consulta.order_by(CitCita.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "creado": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                    "url": url_for("cit_citas.detail", cit_cita_id=resultado.id),
                },
                "cit_cliente": {
                    "email": resultado.cit_cliente.email,
                    "url": (
                        url_for("cit_clientes.detail", cit_cliente_id=resultado.cit_cliente.id)
                        if current_user.can_view("CIT CLIENTES")
                        else ""
                    ),
                },
                "cit_cliente_nombre": resultado.cit_cliente.nombre,
                "cit_servicio": {
                    "clave": resultado.cit_servicio.clave,
                    "descripcion": resultado.cit_servicio.descripcion,
                    "url": (
                        url_for("cit_servicios.detail", cit_servicio_id=resultado.cit_servicio.id)
                        if current_user.can_view("CIT SERVICIOS")
                        else ""
                    ),
                },
                "oficina": {
                    "clave": resultado.oficina.clave,
                    "descripcion": resultado.oficina.descripcion,
                    "url": (
                        url_for("oficinas.detail", oficina_id=resultado.oficina.id) if current_user.can_view("OFICINAS") else ""
                    ),
                },
                "creado": resultado.creado.strftime("%Y-%m-%dT%H:%M:%S"),
                "fecha": resultado.inicio.strftime("%Y-%m-%d 00:00:00"),
                "inicio": resultado.inicio.strftime("%H:%M"),
                "termino": resultado.termino.strftime("%H:%M"),
                "estado": resultado.estado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cit_citas.route("/cit_citas")
def list_active():
    """Listado de Cit Citas activas"""
    return render_template(
        "cit_citas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Citas",
        estatus="A",
    )


@cit_citas.route("/cit_citas/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Cit Citas inactivas"""
    return render_template(
        "cit_citas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Citas inactivas",
        estatus="B",
    )


@cit_citas.route("/cit_citas/<cit_cita_id>")
def detail(cit_cita_id):
    """Detalle de un Cit Cita"""
    cit_cita_id = safe_uuid(cit_cita_id)
    if cit_cita_id == "":
        abort(400)
    cit_cita = CitCita.query.get_or_404(cit_cita_id)
    return render_template("cit_citas/detail.jinja2", cit_cita=cit_cita)
