"""
Ban Bloqueados, formularios
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class BanBloqueadoForm(FlaskForm):
    """Formulario BanBloqueado"""

    ban_tipo = SelectField("Tipo de baneo", coerce=int, validators=[DataRequired()])  # Las opciones se cargan en la vista
    direccion_ip = StringField("Dirección IP (si se llena, se bloquea la IP)", validators=[Optional(), Length(max=45)])
    email = StringField("Email (si se llena, se bloquea la cuenta)", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")
