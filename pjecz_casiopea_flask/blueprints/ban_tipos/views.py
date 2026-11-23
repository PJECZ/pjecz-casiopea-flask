"""
Ban Tipos, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_string
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .forms import BanTipoForm
from .models import BanTipo

MODULO = "BAN TIPOS"

ban_tipos = Blueprint("ban_tipos", __name__, template_folder="templates")


@ban_tipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@ban_tipos.route("/ban_tipos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Ban Tipos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = BanTipo.query.filter(BanTipo.estatus == "A")
    # Filtrar por columnas propias
    if "clave" in request.form:
        clave = safe_clave(request.form["clave"], max_len=32, separator="_")
        if clave != "":
            consulta = consulta.filter(BanTipo.clave.contains(clave))
    if "descripcion" in request.form:
        descripcion = safe_string(request.form["descripcion"], save_enie=True, to_uppercase=False)
        if descripcion != "":
            consulta = consulta.filter(BanTipo.descripcion.ilike(f"%{descripcion}%"))
    # Ordenar y paginar
    registros = consulta.order_by(BanTipo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("ban_tipos.detail", ban_tipo_id=resultado.id),
                },
                "clave": resultado.clave,
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@ban_tipos.route("/ban_tipos")
def list_active():
    """Listado de Ban Tipos"""
    return render_template(
        "ban_tipos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tipos de Baneos",
        estatus="A",
    )


@ban_tipos.route("/ban_tipos/<int:ban_tipo_id>")
def detail(ban_tipo_id):
    """Detalle de un Ban Tipo"""
    ban_tipo = BanTipo.query.get_or_404(ban_tipo_id)
    return render_template("ban_tipos/detail.jinja2", ban_tipo=ban_tipo)


@ban_tipos.route("/ban_tipos/edicion/<int:ban_tipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(ban_tipo_id):
    """Editar Ban Tipo"""
    ban_tipo = BanTipo.query.get_or_404(ban_tipo_id)
    form = BanTipoForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar clave
        clave = safe_clave(form.clave.data, max_len=32, separator="_")
        if clave == "":
            es_valido = False
            flash("La clave es incorrecta o está vacía", "warning")
        # Validar descripción
        descripcion = safe_string(form.descripcion.data, save_enie=True, max_len=128, to_uppercase=False)
        if descripcion == "":
            es_valido = False
            flash("La descripción es incorrecta o está vacía", "warning")
        # Si es válido, actualizar
        if es_valido:
            ban_tipo.clave = clave
            ban_tipo.descripcion = descripcion
            ban_tipo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Tipo de Baneo {ban_tipo.clave}"),
                url=url_for("ban_tipos.detail", ban_tipo_id=ban_tipo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = ban_tipo.clave
    form.descripcion.data = ban_tipo.descripcion
    return render_template("ban_tipos/edit.jinja2", form=form, ban_tipo=ban_tipo)
