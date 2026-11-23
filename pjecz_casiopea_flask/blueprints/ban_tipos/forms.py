"""
Ban Tipos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class BanTipoForm(FlaskForm):
    """Formulario BanTipo"""

    clave = StringField("Clave", validators=[DataRequired(), Regexp(r"^[a-zA-Z0-9_]{1,32}$"), Length(max=32)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=128)])
    guardar = SubmitField("Guardar")
