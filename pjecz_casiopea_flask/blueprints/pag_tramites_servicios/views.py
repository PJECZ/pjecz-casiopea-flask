"""
Pag Trámites Servicios, vistas
"""

import json

from flask import Blueprint, abort, render_template, request, url_for
from flask_login import login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_string, safe_uuid
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..usuarios.models import Usuario
from .models import PagTramiteServicio

MODULO = "PAG TRAMITES SERVICIOS"

pag_tramites_servicios = Blueprint("pag_tramites_servicios", __name__, template_folder="templates")


@pag_tramites_servicios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@pag_tramites_servicios.route("/pag_tramites_servicios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de PagTramitesServicios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = PagTramiteServicio.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(PagTramiteServicio.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(PagTramiteServicio.estatus == "A")
    if "clave" in request.form:
        clave = safe_clave(request.form["clave"])
        if clave != "":
            consulta = consulta.filter(PagTramiteServicio.clave.contains(clave))
    if "descripcion" in request.form:
        descripcion = safe_string(request.form["descripcion"], save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(PagTramiteServicio.descripcion.contains(descripcion))
    # Ordenar y paginar
    registros = consulta.order_by(PagTramiteServicio.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("pag_tramites_servicios.detail", pag_tramite_servicio_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
                "costo": resultado.costo,
                "url": resultado.url,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@pag_tramites_servicios.route("/pag_tramites_servicios")
def list_active():
    """Listado de PagTramitesServicios activos"""
    return render_template(
        "pag_tramites_servicios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Trámites y Servicios",
        estatus="A",
    )


@pag_tramites_servicios.route("/pag_tramites_servicios/inactivos")
def list_inactive():
    """Listado de PagTramitesServicios inactivos"""
    return render_template(
        "pag_tramites_servicios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Trámites y Servicios incativos",
        estatus="B",
    )


@pag_tramites_servicios.route("/pag_tramites_servicios/<pag_tramite_servicio_id>")
def detail(pag_tramite_servicio_id):
    """Detalle de PagTramiteServicio"""
    pag_tramite_servicio_id = safe_uuid(pag_tramite_servicio_id)
    if pag_tramite_servicio_id == "":
        abort(400)
    pag_tramite_servicio = PagTramiteServicio.query.get_or_404(pag_tramite_servicio_id)
    return render_template(
        "pag_tramites_servicios/detail.jinja2",
        pag_tramite_servicio=pag_tramite_servicio,
    )
