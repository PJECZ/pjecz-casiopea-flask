"""
Ban Bloqueados, vistas
"""

import ipaddress
import json
import re
from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_email, safe_message
from ..ban_tipos.models import BanTipo
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .forms import BanBloqueadoForm
from .models import BanBloqueado

MODULO = "BAN BLOQUEADOS"

ban_bloqueados = Blueprint("ban_bloqueados", __name__, template_folder="templates")


@ban_bloqueados.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


def cargar_opciones_ban_tipo(form):
    """Cargar en el formulario los tipos de baneo activos"""
    ban_tipos = BanTipo.query.filter_by(estatus="A").order_by(BanTipo.id).all()
    form.ban_tipo.choices = [(ban_tipo.id, f"{ban_tipo.clave}: {ban_tipo.descripcion}") for ban_tipo in ban_tipos]


def validar_direccion_ip_y_email(form):
    """Validar y normalizar la dirección IP y el email del formulario. Entrega (es_valido, direccion_ip, email)"""
    es_valido = True
    # Validar dirección IP, es opcional
    direccion_ip = None
    if form.direccion_ip.data and form.direccion_ip.data.strip() != "":
        try:
            direccion_ip = str(ipaddress.ip_address(form.direccion_ip.data.strip()))
        except ValueError:
            es_valido = False
            flash("La dirección IP es incorrecta", "warning")
    # Validar email, es opcional
    email = None
    if form.email.data and form.email.data.strip() != "":
        try:
            email = safe_email(form.email.data)
        except ValueError:
            es_valido = False
            flash("El email es incorrecto", "warning")
    # Debe haber al menos uno de los dos, de lo contrario no habría a quién bloquear
    if es_valido and direccion_ip is None and email is None:
        es_valido = False
        flash("Debe indicar una dirección IP, un email o ambos", "warning")
    return es_valido, direccion_ip, email


def buscar_duplicado(direccion_ip, email, excluir_id=None):
    """Buscar un bloqueo activo con la misma combinación de dirección IP y email"""
    consulta = BanBloqueado.query.filter_by(direccion_ip=direccion_ip, email=email, estatus="A")
    if excluir_id is not None:
        consulta = consulta.filter(BanBloqueado.id != excluir_id)
    return consulta.first()


def obtener_ban_tipo(form):
    """Tomar el tipo de baneo elegido, solo si está activo"""
    ban_tipo = BanTipo.query.filter_by(id=form.ban_tipo.data, estatus="A").first()
    if ban_tipo is None:
        flash("El tipo de baneo no es válido", "warning")
    return ban_tipo


def descripcion_bloqueado(ban_bloqueado):
    """Texto corto para la bitácora con a quién se bloquea"""
    partes = [parte for parte in (ban_bloqueado.direccion_ip, ban_bloqueado.email) if parte]
    return " / ".join(partes)


@ban_bloqueados.route("/ban_bloqueados/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Ban Bloqueados"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = BanBloqueado.query
    # Filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(BanBloqueado.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(BanBloqueado.estatus == "A")
    if "ban_tipo_id" in request.form and request.form["ban_tipo_id"].isdigit():
        consulta = consulta.filter(BanBloqueado.ban_tipo_id == int(request.form["ban_tipo_id"]))
    if "fecha_inicio" in request.form:
        try:
            fecha_inicio = datetime.strptime(request.form["fecha_inicio"], "%Y-%m-%d")
            consulta = consulta.filter(BanBloqueado.tiempo >= fecha_inicio)
        except ValueError:
            pass
    if "fecha_termino" in request.form:
        try:
            fecha_termino = datetime.strptime(request.form["fecha_termino"], "%Y-%m-%d") + timedelta(days=1)
            consulta = consulta.filter(BanBloqueado.tiempo < fecha_termino)
        except ValueError:
            pass
    if "direccion_ip" in request.form:
        direccion_ip = re.sub(r"[^0-9a-fA-F.:]", "", request.form["direccion_ip"])[:45].lower()
        if direccion_ip != "":
            consulta = consulta.filter(BanBloqueado.direccion_ip.contains(direccion_ip))
    if "email" in request.form:
        email = safe_email(request.form["email"], search_fragment=True)
        if email:
            consulta = consulta.filter(BanBloqueado.email.contains(email))
    # Ordenar y paginar
    registros = consulta.order_by(BanBloqueado.tiempo.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "fecha": resultado.tiempo.strftime("%Y-%m-%d"),
                    "hora": resultado.tiempo.strftime("%I:%M:%S ") + ("AM" if resultado.tiempo.hour < 12 else "PM"),
                    "url": url_for("ban_bloqueados.detail", ban_bloqueado_id=resultado.id),
                },
                "ban_tipo": {
                    "clave": resultado.ban_tipo.clave,
                    "descripcion": resultado.ban_tipo.descripcion,
                    "url": (
                        url_for("ban_tipos.detail", ban_tipo_id=resultado.ban_tipo_id) if current_user.can_view("BAN TIPOS") else ""
                    ),
                },
                "direccion_ip": resultado.direccion_ip or "",
                "email": resultado.email or "",
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@ban_bloqueados.route("/ban_bloqueados")
def list_active():
    """Listado de Ban Bloqueados activos"""
    return render_template(
        "ban_bloqueados/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Bloqueados",
        estatus="A",
        ban_tipos=BanTipo.query.filter_by(estatus="A").order_by(BanTipo.id).all(),
    )


@ban_bloqueados.route("/ban_bloqueados/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Ban Bloqueados inactivos"""
    return render_template(
        "ban_bloqueados/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Bloqueados inactivos",
        estatus="B",
        ban_tipos=BanTipo.query.filter_by(estatus="A").order_by(BanTipo.id).all(),
    )


@ban_bloqueados.route("/ban_bloqueados/<int:ban_bloqueado_id>")
def detail(ban_bloqueado_id):
    """Detalle de un Ban Bloqueado"""
    ban_bloqueado = BanBloqueado.query.get_or_404(ban_bloqueado_id)
    return render_template("ban_bloqueados/detail.jinja2", ban_bloqueado=ban_bloqueado)


@ban_bloqueados.route("/ban_bloqueados/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Ban Bloqueado"""
    form = BanBloqueadoForm()
    cargar_opciones_ban_tipo(form)
    if form.validate_on_submit():
        es_valido, direccion_ip, email = validar_direccion_ip_y_email(form)
        ban_tipo = obtener_ban_tipo(form)
        # Evitar duplicados activos para la misma combinación de IP y email
        if es_valido:
            existente = buscar_duplicado(direccion_ip, email)
            if existente:
                flash("Ya existe un bloqueo activo para esa dirección IP y email", "warning")
                return redirect(url_for("ban_bloqueados.detail", ban_bloqueado_id=existente.id))
        # Si es válido, guardar
        if es_valido and ban_tipo is not None:
            ban_bloqueado = BanBloqueado(ban_tipo_id=ban_tipo.id, direccion_ip=direccion_ip, email=email, tiempo=datetime.now())
            ban_bloqueado.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Bloqueado {descripcion_bloqueado(ban_bloqueado)}"),
                url=url_for("ban_bloqueados.detail", ban_bloqueado_id=ban_bloqueado.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("ban_bloqueados/new.jinja2", form=form)


@ban_bloqueados.route("/ban_bloqueados/edicion/<int:ban_bloqueado_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(ban_bloqueado_id):
    """Editar Ban Bloqueado"""
    ban_bloqueado = BanBloqueado.query.get_or_404(ban_bloqueado_id)
    form = BanBloqueadoForm()
    cargar_opciones_ban_tipo(form)
    if form.validate_on_submit():
        es_valido, direccion_ip, email = validar_direccion_ip_y_email(form)
        ban_tipo = obtener_ban_tipo(form)
        # Evitar que quede igual a otro bloqueo activo
        if es_valido:
            existente = buscar_duplicado(direccion_ip, email, excluir_id=ban_bloqueado.id)
            if existente:
                es_valido = False
                flash(f"Ya existe otro bloqueo activo (id {existente.id}) para esa dirección IP y email", "warning")
        # Si es válido, actualizar
        if es_valido and ban_tipo is not None:
            ban_bloqueado.ban_tipo_id = ban_tipo.id
            ban_bloqueado.direccion_ip = direccion_ip
            ban_bloqueado.email = email
            ban_bloqueado.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Bloqueado {descripcion_bloqueado(ban_bloqueado)}"),
                url=url_for("ban_bloqueados.detail", ban_bloqueado_id=ban_bloqueado.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    elif request.method == "GET":
        form.ban_tipo.data = ban_bloqueado.ban_tipo_id
        form.direccion_ip.data = ban_bloqueado.direccion_ip
        form.email.data = ban_bloqueado.email
    return render_template("ban_bloqueados/edit.jinja2", form=form, ban_bloqueado=ban_bloqueado)


@ban_bloqueados.route("/ban_bloqueados/eliminar/<int:ban_bloqueado_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(ban_bloqueado_id):
    """Eliminar Ban Bloqueado"""
    ban_bloqueado = BanBloqueado.query.get_or_404(ban_bloqueado_id)
    if ban_bloqueado.estatus == "A":
        ban_bloqueado.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Bloqueado {descripcion_bloqueado(ban_bloqueado)}"),
            url=url_for("ban_bloqueados.detail", ban_bloqueado_id=ban_bloqueado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("ban_bloqueados.detail", ban_bloqueado_id=ban_bloqueado.id))


@ban_bloqueados.route("/ban_bloqueados/recuperar/<int:ban_bloqueado_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(ban_bloqueado_id):
    """Recuperar Ban Bloqueado"""
    ban_bloqueado = BanBloqueado.query.get_or_404(ban_bloqueado_id)
    if ban_bloqueado.estatus == "B":
        ban_bloqueado.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Bloqueado {descripcion_bloqueado(ban_bloqueado)}"),
            url=url_for("ban_bloqueados.detail", ban_bloqueado_id=ban_bloqueado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("ban_bloqueados.detail", ban_bloqueado_id=ban_bloqueado.id))
