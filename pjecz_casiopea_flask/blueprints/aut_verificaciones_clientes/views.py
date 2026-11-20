"""
Aut Verificaciones Clientes, vistas
"""

import json
import re
from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..cit_clientes.models import CitCliente
from .models import AutVerificacionCliente

MODULO = "AUT VERIFICACIONES CLIENTES"

# Número de intentos a partir del cual se considera Máx Intentos
MAXIMO_INTENTOS = 5

aut_verificaciones_clientes = Blueprint("aut_verificaciones_clientes", __name__, template_folder="templates")


def estatus_verificacion(verificacion):
    """Entrega el estado de una verificación: UTILIZADO, MAX_INTENTOS, EN_ESPERA o CADUCADO"""
    if verificacion.utilizado:
        return "UTILIZADO"
    if verificacion.intentos > MAXIMO_INTENTOS:
        return "MAX_INTENTOS"
    if verificacion.tiempo_caducidad >= datetime.now():
        return "EN_ESPERA"
    return "CADUCADO"


@aut_verificaciones_clientes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@aut_verificaciones_clientes.route("/aut_verificaciones_clientes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Aut Verificaciones Clientes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = AutVerificacionCliente.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(AutVerificacionCliente.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(AutVerificacionCliente.estatus == "A")
    if "fecha_inicio" in request.form:
        try:
            fecha_inicio = datetime.strptime(request.form["fecha_inicio"], "%Y-%m-%d")
            consulta = consulta.filter(AutVerificacionCliente.creado >= fecha_inicio)
        except ValueError:
            pass
    if "fecha_termino" in request.form:
        try:
            fecha_termino = datetime.strptime(request.form["fecha_termino"], "%Y-%m-%d") + timedelta(days=1)
            consulta = consulta.filter(AutVerificacionCliente.creado < fecha_termino)
        except ValueError:
            pass
    if "telefono" in request.form:
        telefono = re.sub(r"[^0-9]", "", request.form["telefono"])[:20]
        if telefono != "":
            consulta = consulta.filter(AutVerificacionCliente.telefono.contains(telefono))
    if "direccion_ip" in request.form:
        direccion_ip = re.sub(r"[^0-9a-fA-F.:]", "", request.form["direccion_ip"])[:45].lower()
        if direccion_ip != "":
            consulta = consulta.filter(AutVerificacionCliente.direccion_ip.contains(direccion_ip))
    if "estado" in request.form:
        ahora = datetime.now()
        estado = request.form["estado"]
        if estado == "UTILIZADO":
            consulta = consulta.filter(AutVerificacionCliente.utilizado.is_(True))
        elif estado == "MAX_INTENTOS":
            consulta = consulta.filter(AutVerificacionCliente.utilizado.is_(False))
            consulta = consulta.filter(AutVerificacionCliente.intentos > MAXIMO_INTENTOS)
        elif estado == "EN_ESPERA":
            consulta = consulta.filter(AutVerificacionCliente.utilizado.is_(False))
            consulta = consulta.filter(AutVerificacionCliente.intentos <= MAXIMO_INTENTOS)
            consulta = consulta.filter(AutVerificacionCliente.tiempo_caducidad >= ahora)
        elif estado == "CADUCADO":
            consulta = consulta.filter(AutVerificacionCliente.utilizado.is_(False))
            consulta = consulta.filter(AutVerificacionCliente.intentos <= MAXIMO_INTENTOS)
            consulta = consulta.filter(AutVerificacionCliente.tiempo_caducidad < ahora)
    # Luego filtrar por columnas de otras tablas
    if "email" in request.form:
        email = safe_email(request.form["email"], search_fragment=True)
        if email:
            consulta = consulta.filter(AutVerificacionCliente.email.contains(email))
    elif "nombre_completo" in request.form:
        nombre_completo = safe_string(request.form["nombre_completo"], save_enie=True)
        if nombre_completo:
            consulta = consulta.join(CitCliente)
            for palabra in nombre_completo.split():
                consulta = consulta.filter(
                    or_(
                        CitCliente.nombres.contains(palabra),
                        CitCliente.apellido_primero.contains(palabra),
                        CitCliente.apellido_segundo.contains(palabra),
                    )
                )
    # Ordenar y paginar
    registros = consulta.order_by(AutVerificacionCliente.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "fecha": resultado.creado.strftime("%Y-%m-%d"),
                    "hora": resultado.creado.strftime("%I:%M:%S ") + ("AM" if resultado.creado.hour < 12 else "PM"),
                    "url": url_for("aut_verificaciones_clientes.detail", aut_verificacion_cliente_id=resultado.id),
                },
                "cit_cliente": {
                    "nombre": resultado.cit_cliente.nombre,
                    "telefono": resultado.telefono or "",
                    "email": resultado.email or "",
                    "url": (
                        url_for("cit_clientes.detail", cit_cliente_id=resultado.cit_cliente.id) if current_user.can_view("CIT CLIENTES") else ""
                    ),
                },
                "codigo_verificacion": resultado.codigo_verificacion,
                "estatus_verificacion": estatus_verificacion(resultado),
                "conexion": {
                    "direccion_ip": resultado.direccion_ip or "",
                    "dispositivo": resultado.dispositivo or "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@aut_verificaciones_clientes.route("/aut_verificaciones_clientes")
def list_active():
    """Listado de Aut Verificaciones Clientes activas"""
    return render_template(
        "aut_verificaciones_clientes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Verificaciones de Accesos de Clientes",
        estatus="A",
    )


@aut_verificaciones_clientes.route("/aut_verificaciones_clientes/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Aut Verificaciones Clientes inactivas"""
    return render_template(
        "aut_verificaciones_clientes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Verificaciones de Accesos de Clientes inactivas",
        estatus="B",
    )


@aut_verificaciones_clientes.route("/aut_verificaciones_clientes/<aut_verificacion_cliente_id>")
def detail(aut_verificacion_cliente_id):
    """Detalle de una Aut Verificación Cliente"""
    aut_verificacion_cliente_id = safe_uuid(aut_verificacion_cliente_id)
    if aut_verificacion_cliente_id == "":
        abort(400)
    aut_verificacion_cliente = AutVerificacionCliente.query.get_or_404(aut_verificacion_cliente_id)
    return render_template(
        "aut_verificaciones_clientes/detail.jinja2",
        aut_verificacion_cliente=aut_verificacion_cliente,
        estatus_verificacion=estatus_verificacion(aut_verificacion_cliente),
    )


@aut_verificaciones_clientes.route("/aut_verificaciones_clientes/eliminar/<aut_verificacion_cliente_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(aut_verificacion_cliente_id):
    """Eliminar Aut Verificación Cliente"""
    aut_verificacion_cliente_id = safe_uuid(aut_verificacion_cliente_id)
    if aut_verificacion_cliente_id == "":
        abort(400)
    aut_verificacion_cliente = AutVerificacionCliente.query.get_or_404(aut_verificacion_cliente_id)
    if aut_verificacion_cliente.estatus == "A":
        aut_verificacion_cliente.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada Verificación del cliente {aut_verificacion_cliente.cit_cliente.email}"),
            url=url_for("aut_verificaciones_clientes.detail", aut_verificacion_cliente_id=aut_verificacion_cliente.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("aut_verificaciones_clientes.detail", aut_verificacion_cliente_id=aut_verificacion_cliente.id))


@aut_verificaciones_clientes.route("/aut_verificaciones_clientes/recuperar/<aut_verificacion_cliente_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(aut_verificacion_cliente_id):
    """Recuperar Aut Verificación Cliente"""
    aut_verificacion_cliente_id = safe_uuid(aut_verificacion_cliente_id)
    if aut_verificacion_cliente_id == "":
        abort(400)
    aut_verificacion_cliente = AutVerificacionCliente.query.get_or_404(aut_verificacion_cliente_id)
    if aut_verificacion_cliente.estatus == "B":
        aut_verificacion_cliente.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada Verificación del cliente {aut_verificacion_cliente.cit_cliente.email}"),
            url=url_for("aut_verificaciones_clientes.detail", aut_verificacion_cliente_id=aut_verificacion_cliente.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("aut_verificaciones_clientes.detail", aut_verificacion_cliente_id=aut_verificacion_cliente.id))
