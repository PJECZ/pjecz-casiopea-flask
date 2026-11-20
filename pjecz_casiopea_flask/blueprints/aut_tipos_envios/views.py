"""
Aut Tipos Envíos, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_message, safe_string
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .forms import AutTipoEnvioForm
from .models import AutTipoEnvio

MODULO = "AUT TIPOS ENVIOS"

aut_tipos_envios = Blueprint("aut_tipos_envios", __name__, template_folder="templates")


@aut_tipos_envios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@aut_tipos_envios.route("/aut_tipos_envios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Aut Tipos Envíos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = AutTipoEnvio.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(AutTipoEnvio.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(AutTipoEnvio.estatus == "A")
    if "descripcion" in request.form:
        descripcion = safe_string(request.form["descripcion"], save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(AutTipoEnvio.descripcion.contains(descripcion))
    # Ordenar y paginar
    registros = consulta.order_by(AutTipoEnvio.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("aut_tipos_envios.detail", aut_tipo_envio_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
                "toggle_activo": {
                    "id": resultado.id,
                    "es_activo": resultado.activo,
                    "url": (
                        url_for("aut_tipos_envios.toggle_activo_json", aut_tipo_envio_id=resultado.id)
                        if current_user.can_edit(MODULO)
                        else ""
                    ),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@aut_tipos_envios.route("/aut_tipos_envios")
def list_active():
    """Listado de Aut Tipos Envíos activos"""
    return render_template(
        "aut_tipos_envios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Tipos de Envíos",
        estatus="A",
    )


@aut_tipos_envios.route("/aut_tipos_envios/<int:aut_tipo_envio_id>")
def detail(aut_tipo_envio_id):
    """Detalle de un Aut Tipo Envío"""
    aut_tipo_envio = AutTipoEnvio.query.get_or_404(aut_tipo_envio_id)
    return render_template("aut_tipos_envios/detail.jinja2", aut_tipo_envio=aut_tipo_envio)


@aut_tipos_envios.route("/aut_tipos_envios/edicion/<int:aut_tipo_envio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(aut_tipo_envio_id):
    """Editar Aut Tipo Envío"""
    aut_tipo_envio = AutTipoEnvio.query.get_or_404(aut_tipo_envio_id)
    form = AutTipoEnvioForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar descripción
        descripcion = safe_string(form.descripcion.data, save_enie=True, max_len=32)
        if descripcion == "":
            es_valido = False
            flash("La descripción es incorrecta o está vacía", "warning")
        # Si es válido, actualizar
        if es_valido:
            aut_tipo_envio.descripcion = descripcion
            aut_tipo_envio.activo = form.activo.data
            aut_tipo_envio.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Tipo de Envío {aut_tipo_envio.descripcion}"),
                url=url_for("aut_tipos_envios.detail", aut_tipo_envio_id=aut_tipo_envio.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.descripcion.data = aut_tipo_envio.descripcion
    form.activo.data = aut_tipo_envio.activo
    return render_template("aut_tipos_envios/edit.jinja2", form=form, aut_tipo_envio=aut_tipo_envio)


@aut_tipos_envios.route("/aut_tipos_envios/toggle_activo_json/<int:aut_tipo_envio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def toggle_activo_json(aut_tipo_envio_id):
    """Cambiar activo a su opuesto al dar clic a su boton en datatable"""
    aut_tipo_envio = AutTipoEnvio.query.get_or_404(aut_tipo_envio_id)
    aut_tipo_envio.activo = not aut_tipo_envio.activo
    aut_tipo_envio.save()
    # Entregar JSON (la clave es_activo la espera datatables-toggles.js)
    return {
        "success": True,
        "message": "Activo" if aut_tipo_envio.activo else "Inactivo",
        "es_activo": aut_tipo_envio.activo,
        "id": aut_tipo_envio.id,
    }
