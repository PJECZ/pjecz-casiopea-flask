"""
Ban Bloqueados, formularios
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class BanBloqueadoForm(FlaskForm):
    """Formulario BanBloqueado"""

    ban_tipo = SelectField("Tipo de baneo", coerce=int, validators=[DataRequired()])  # Las opciones se cargan en la vista
    direccion_ip = StringField("Dirección IP", validators=[Optional(), Length(max=45)], render_kw={"placeholder": "Ej. 189.203.10.25"})
    email = StringField("Email", validators=[Optional(), Length(max=256)], render_kw={"placeholder": "Ej. usuario@ejemplo.com"})
    guardar = SubmitField("Guardar")
