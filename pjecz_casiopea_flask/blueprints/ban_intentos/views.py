"""
Ban Intentos, vistas
"""

import json
import re
from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .models import BanIntento

MODULO = "BAN INTENTOS"

ban_intentos = Blueprint("ban_intentos", __name__, template_folder="templates")


@ban_intentos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@ban_intentos.route("/ban_intentos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Ban Intentos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = BanIntento.query
    # Filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(BanIntento.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(BanIntento.estatus == "A")
    if "fecha_inicio" in request.form:
        try:
            fecha_inicio = datetime.strptime(request.form["fecha_inicio"], "%Y-%m-%d")
            consulta = consulta.filter(BanIntento.tiempo >= fecha_inicio)
        except ValueError:
            pass
    if "fecha_termino" in request.form:
        try:
            fecha_termino = datetime.strptime(request.form["fecha_termino"], "%Y-%m-%d") + timedelta(days=1)
            consulta = consulta.filter(BanIntento.tiempo < fecha_termino)
        except ValueError:
            pass
    if "direccion_ip" in request.form:
        direccion_ip = re.sub(r"[^0-9a-fA-F.:]", "", request.form["direccion_ip"])[:45].lower()
        if direccion_ip != "":
            consulta = consulta.filter(BanIntento.direccion_ip.contains(direccion_ip))
    if "email" in request.form:
        email = safe_email(request.form["email"], search_fragment=True)
        if email:
            consulta = consulta.filter(BanIntento.email.contains(email))
    # Ordenar y paginar
    registros = consulta.order_by(BanIntento.tiempo.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "fecha": resultado.tiempo.strftime("%Y-%m-%d"),
                    "hora": resultado.tiempo.strftime("%I:%M:%S ") + ("AM" if resultado.tiempo.hour < 12 else "PM"),
                    "url": url_for("ban_intentos.detail", ban_intento_id=resultado.id),
                },
                "email": resultado.email,
                "direccion_ip": resultado.direccion_ip,
                "intentos": resultado.intentos,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@ban_intentos.route("/ban_intentos")
def list_active():
    """Listado de Ban Intentos activos"""
    return render_template(
        "ban_intentos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Intentos de Acceso",
        estatus="A",
    )


@ban_intentos.route("/ban_intentos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Ban Intentos inactivos"""
    return render_template(
        "ban_intentos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Intentos de Acceso inactivos",
        estatus="B",
    )


@ban_intentos.route("/ban_intentos/<int:ban_intento_id>")
def detail(ban_intento_id):
    """Detalle de un Ban Intento"""
    ban_intento = BanIntento.query.get_or_404(ban_intento_id)
    return render_template("ban_intentos/detail.jinja2", ban_intento=ban_intento)


@ban_intentos.route("/ban_intentos/eliminar/<int:ban_intento_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(ban_intento_id):
    """Eliminar Ban Intento"""
    ban_intento = BanIntento.query.get_or_404(ban_intento_id)
    if ban_intento.estatus == "A":
        ban_intento.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Intento de Acceso de {ban_intento.email} desde {ban_intento.direccion_ip}"),
            url=url_for("ban_intentos.detail", ban_intento_id=ban_intento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("ban_intentos.detail", ban_intento_id=ban_intento.id))


@ban_intentos.route("/ban_intentos/recuperar/<int:ban_intento_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(ban_intento_id):
    """Recuperar Ban Intento"""
    ban_intento = BanIntento.query.get_or_404(ban_intento_id)
    if ban_intento.estatus == "B":
        ban_intento.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Intento de Acceso de {ban_intento.email} desde {ban_intento.direccion_ip}"),
            url=url_for("ban_intentos.detail", ban_intento_id=ban_intento.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("ban_intentos.detail", ban_intento_id=ban_intento.id))
