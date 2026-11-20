"""
Aut Tipos Envíos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class AutTipoEnvioForm(FlaskForm):
    """Formulario AutTipoEnvio"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=32)])
    activo = BooleanField("Activo", validators=[Optional()], default=True)
    guardar = SubmitField("Guardar")
