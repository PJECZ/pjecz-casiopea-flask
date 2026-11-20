"""
Aut Verificaciones Usuarios, vistas
"""

import json
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..usuarios.models import Usuario
from .models import AutVerificacionUsuario

MODULO = "AUT VERIFICACIONES USUARIOS"

# Número de intentos a partir del cual se considera Máx Intentos
MAXIMO_INTENTOS = 5

aut_verificaciones_usuarios = Blueprint("aut_verificaciones_usuarios", __name__, template_folder="templates")


def estatus_verificacion(verificacion):
    """Entrega el estado de una verificación: UTILIZADO, MAX_INTENTOS, EN_ESPERA o NO_UTILIZADO"""
    if verificacion.utilizado:
        return "UTILIZADO"
    if verificacion.intentos > MAXIMO_INTENTOS:
        return "MAX_INTENTOS"
    if verificacion.tiempo_caducidad >= datetime.now():
        return "EN_ESPERA"
    return "NO_UTILIZADO"


@aut_verificaciones_usuarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@aut_verificaciones_usuarios.route("/aut_verificaciones_usuarios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Aut Verificaciones Usuarios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = AutVerificacionUsuario.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(AutVerificacionUsuario.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(AutVerificacionUsuario.estatus == "A")
    # Luego filtrar por columnas de otras tablas
    if "email" in request.form:
        email = safe_email(request.form["email"], search_fragment=True)
        if email:
            consulta = consulta.join(Usuario)
            consulta = consulta.filter(Usuario.email.contains(email))
    elif "nombre_completo" in request.form:
        nombre_completo = safe_string(request.form["nombre_completo"], save_enie=True)
        if nombre_completo:
            consulta = consulta.join(Usuario)
            for palabra in nombre_completo.split():
                consulta = consulta.filter(
                    or_(
                        Usuario.nombres.contains(palabra),
                        Usuario.apellido_paterno.contains(palabra),
                        Usuario.apellido_materno.contains(palabra),
                    )
                )
    # Ordenar y paginar
    registros = consulta.order_by(AutVerificacionUsuario.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "creado": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                    "url": url_for("aut_verificaciones_usuarios.detail", aut_verificacion_usuario_id=resultado.id),
                },
                "usuario": {
                    "nombre": resultado.usuario.nombre,
                    "email": resultado.usuario.email,
                    "url": (
                        url_for("usuarios.detail", usuario_id=resultado.usuario.id) if current_user.can_view("USUARIOS") else ""
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


@aut_verificaciones_usuarios.route("/aut_verificaciones_usuarios")
def list_active():
    """Listado de Aut Verificaciones Usuarios activas"""
    return render_template(
        "aut_verificaciones_usuarios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Verificaciones de Acceso de Usuarios",
        estatus="A",
    )


@aut_verificaciones_usuarios.route("/aut_verificaciones_usuarios/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Aut Verificaciones Usuarios inactivas"""
    return render_template(
        "aut_verificaciones_usuarios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Verificaciones de Acceso de Usuarios inactivas",
        estatus="B",
    )


@aut_verificaciones_usuarios.route("/aut_verificaciones_usuarios/<aut_verificacion_usuario_id>")
def detail(aut_verificacion_usuario_id):
    """Detalle de una Aut Verificación Usuario"""
    aut_verificacion_usuario_id = safe_uuid(aut_verificacion_usuario_id)
    if aut_verificacion_usuario_id == "":
        abort(400)
    aut_verificacion_usuario = AutVerificacionUsuario.query.get_or_404(aut_verificacion_usuario_id)
    return render_template(
        "aut_verificaciones_usuarios/detail.jinja2",
        aut_verificacion_usuario=aut_verificacion_usuario,
        estatus_verificacion=estatus_verificacion(aut_verificacion_usuario),
    )


@aut_verificaciones_usuarios.route("/aut_verificaciones_usuarios/eliminar/<aut_verificacion_usuario_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(aut_verificacion_usuario_id):
    """Eliminar Aut Verificación Usuario"""
    aut_verificacion_usuario_id = safe_uuid(aut_verificacion_usuario_id)
    if aut_verificacion_usuario_id == "":
        abort(400)
    aut_verificacion_usuario = AutVerificacionUsuario.query.get_or_404(aut_verificacion_usuario_id)
    if aut_verificacion_usuario.estatus == "A":
        aut_verificacion_usuario.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada Verificación del usuario {aut_verificacion_usuario.usuario.email}"),
            url=url_for("aut_verificaciones_usuarios.detail", aut_verificacion_usuario_id=aut_verificacion_usuario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("aut_verificaciones_usuarios.detail", aut_verificacion_usuario_id=aut_verificacion_usuario.id))


@aut_verificaciones_usuarios.route("/aut_verificaciones_usuarios/recuperar/<aut_verificacion_usuario_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(aut_verificacion_usuario_id):
    """Recuperar Aut Verificación Usuario"""
    aut_verificacion_usuario_id = safe_uuid(aut_verificacion_usuario_id)
    if aut_verificacion_usuario_id == "":
        abort(400)
    aut_verificacion_usuario = AutVerificacionUsuario.query.get_or_404(aut_verificacion_usuario_id)
    if aut_verificacion_usuario.estatus == "B":
        aut_verificacion_usuario.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada Verificación del usuario {aut_verificacion_usuario.usuario.email}"),
            url=url_for("aut_verificaciones_usuarios.detail", aut_verificacion_usuario_id=aut_verificacion_usuario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("aut_verificaciones_usuarios.detail", aut_verificacion_usuario_id=aut_verificacion_usuario.id))
