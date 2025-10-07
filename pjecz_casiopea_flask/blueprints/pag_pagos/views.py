"""
Pag Pagos, vistas
"""

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..cit_clientes.models import CitCliente
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .models import PagPago

MODULO = "PAG PAGOS"

pag_pagos = Blueprint("pag_pagos", __name__, template_folder="templates")


@pag_pagos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@pag_pagos.route("/pag_pagos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de PagPagos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = PagPago.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(PagPago.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(PagPago.estatus == "A")
    if "autoridad_id" in request.form:
        consulta = consulta.filter(PagPago.autoridad_id == request.form["autoridad_id"])
    if "cit_cliente_id" in request.form:
        consulta = consulta.filter(PagPago.cit_cliente_id == request.form["cit_cliente_id"])
    if "distrito_id" in request.form:
        consulta = consulta.filter(PagPago.distrito_id == request.form["distrito_id"])
    if "pag_tramite_servicio_id" in request.form:
        consulta = consulta.filter(PagPago.pag_tramite_servicio_id == request.form["pag_tramite_servicio_id"])
    if "estado" in request.form:
        estado = safe_string(request.form["estado"])
        if estado != "":
            consulta = consulta.filter(PagPago.estado == estado)
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
    registros = consulta.order_by(PagPago.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "creado": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                    "url": url_for("pag_pagos.detail", pag_pago_id=resultado.id),
                },
                "cit_cliente": {
                    "email": resultado.cit_cliente.email,
                    "url": (
                        url_for("cit_clientes.detail", cit_cliente_id=resultado.cit_cliente_id)
                        if current_user.can_view("CIT CLIENTES")
                        else ""
                    ),
                },
                "cit_cliente_nombre": resultado.cit_cliente.nombre,
                "pag_tramite_servicio": {
                    "clave": resultado.pag_tramite_servicio.clave,
                    "descripcion": resultado.pag_tramite_servicio.descripcion,
                    "url": (
                        url_for(
                            "pag_tramites_servicios.detail",
                            pag_tramite_servicio_id=resultado.pag_tramite_servicio.id,
                        )
                        if current_user.can_view("PAG TRAMITES SERVICIOS")
                        else ""
                    ),
                },
                "distrito_clave": resultado.distrito.clave,
                "autoridad_clave": resultado.autoridad.clave,
                "estado": resultado.estado,
                "folio": resultado.folio,
                "total": resultado.total,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@pag_pagos.route("/pag_pagos")
def list_active():
    """Listado de pagos activos"""
    return render_template(
        "pag_pagos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Pagos",
        estatus="A",
    )


@pag_pagos.route("/pag_pagos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de pagos inactivos"""
    return render_template(
        "pag_pagos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Pagos inactivos",
        estatus="B",
    )


@pag_pagos.route("/pag_pagos/<pag_pago_id>")
def detail(pag_pago_id):
    """Detalle de un pago"""
    pag_pago_id = safe_uuid(pag_pago_id)
    if pag_pago_id == "":
        abort(400)
    pag_pago = PagPago.query.get_or_404(pag_pago_id)
    return render_template(
        "pag_pagos/detail.jinja2",
        pag_pago=pag_pago,
    )


@pag_pagos.route("/pag_pagos/eliminar/<pag_pago_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(pag_pago_id):
    """Eliminar pago"""
    pag_pago_id = safe_uuid(pag_pago_id)
    if pag_pago_id == "":
        abort(400)
    pag_pago = PagPago.query.get_or_404(pag_pago_id)
    if pag_pago.estatus == "A":
        pag_pago.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado pago {pag_pago.id}"),
            url=url_for("pag_pagos.detail", pag_pago_id=pag_pago.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("pag_pagos.detail", pag_pago_id=pag_pago.id))


@pag_pagos.route("/pag_pagos/recuperar/<pag_pago_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(pag_pago_id):
    """Recuperar Pago"""
    pag_pago_id = safe_uuid(pag_pago_id)
    if pag_pago_id == "":
        abort(400)
    pag_pago = PagPago.query.get_or_404(pag_pago_id)
    if pag_pago.estatus == "B":
        pag_pago.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Pago {pag_pago.id}"),
            url=url_for("pag_pagos.detail", pag_pago_id=pag_pago.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("pag_pagos.detail", pag_pago_id=pag_pago.id))
