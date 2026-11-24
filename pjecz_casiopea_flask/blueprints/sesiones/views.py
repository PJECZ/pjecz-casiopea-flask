"""
Sesiones, vistas
"""

import json
import re
from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ...config.settings import get_settings
from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ..usuarios.models import Usuario
from .models import Sesion

MODULO = "SESIONES"

sesiones = Blueprint("sesiones", __name__, template_folder="templates")


@sesiones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


def limite_de_vigencia() -> datetime:
    """Las sesiones iniciadas antes de este momento ya caducaron"""
    return datetime.now() - timedelta(hours=int(get_settings().SESSION_DURATION_HOURS))


def esta_vigente(sesion: Sesion) -> bool:
    """Una sesión está vigente si está activa y no ha caducado"""
    return sesion.activa and sesion.inicio >= limite_de_vigencia()


def obtener_sesion(sesion_id: str) -> Sesion:
    """Consultar la sesión por su id (el mismo del usuario), 400 si no es un UUID y 404 si no existe"""
    sesion_id = safe_uuid(sesion_id)
    if sesion_id == "":
        abort(400)
    return Sesion.query.get_or_404(sesion_id)


def formato_tiempo(tiempo: datetime) -> dict:
    """Fecha y hora para el DataTable"""
    return {
        "fecha": tiempo.strftime("%Y-%m-%d"),
        "hora": tiempo.strftime("%I:%M:%S ") + ("AM" if tiempo.hour < 12 else "PM"),
    }


@sesiones.route("/sesiones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Sesiones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Sesion.query.join(Usuario)
    # Filtrar por estado: activas (por defecto) son las abiertas y sin caducar, inactivas son las cerradas o caducadas
    estado = request.form.get("estado", "activas")
    if estado == "inactivas":
        consulta = consulta.filter(or_(Sesion.activa.is_(False), Sesion.inicio < limite_de_vigencia()))
    elif estado != "todas":
        consulta = consulta.filter(Sesion.activa.is_(True)).filter(Sesion.inicio >= limite_de_vigencia())
    if "email" in request.form:
        email = safe_email(request.form["email"], search_fragment=True)
        if email:
            consulta = consulta.filter(Usuario.email.contains(email))
    if "direccion_ip" in request.form:
        direccion_ip = re.sub(r"[^0-9a-fA-F.:]", "", request.form["direccion_ip"])[:64].lower()
        if direccion_ip != "":
            consulta = consulta.filter(Sesion.direccion_ip.contains(direccion_ip))
    # Ordenar y paginar
    registros = consulta.order_by(Sesion.ultimo_acceso.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.usuario.nombre,
                    "email": resultado.usuario.email,
                    "url": url_for("sesiones.detail", sesion_id=resultado.id),
                },
                "direccion_ip": resultado.direccion_ip or "",
                "inicio": formato_tiempo(resultado.inicio),
                "ultimo_acceso": formato_tiempo(resultado.ultimo_acceso),
                "vigente": esta_vigente(resultado),
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@sesiones.route("/sesiones")
def list_active():
    """Listado de Sesiones, por defecto las activas; el estado se cambia con el filtro"""
    return render_template(
        "sesiones/list.jinja2",
        filtros=json.dumps({"estado": "activas"}),
        titulo="Sesiones",
    )


@sesiones.route("/sesiones/<sesion_id>")
def detail(sesion_id):
    """Detalle de una Sesión"""
    sesion = obtener_sesion(sesion_id)
    return render_template("sesiones/detail.jinja2", sesion=sesion, vigente=esta_vigente(sesion))


@sesiones.route("/sesiones/cerrar/<sesion_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def close(sesion_id):
    """Cerrar a distancia una Sesión, el usuario deberá volver a entrar"""
    sesion = obtener_sesion(sesion_id)
    if sesion.activa:
        sesion.activa = False
        sesion.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Cerrada la sesión de {sesion.usuario.email}"),
            url=url_for("sesiones.detail", sesion_id=sesion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("sesiones.detail", sesion_id=sesion.id))
