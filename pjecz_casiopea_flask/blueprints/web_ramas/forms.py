"""
Web Ramas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class WebRamaForm(FlaskForm):
    """Formulario WebRama"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    esta_archivado = BooleanField("Está archivado", validators=[Optional()], default=False)
    guardar = SubmitField("Guardar")
