"""
Cit Categorías, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

from ...lib.safe_string import CLAVE_REGEXP


class CitCategoriaForm(FlaskForm):
    """Formulario CitCategoria"""

    clave = StringField("Clave", validators=[DataRequired(), Regexp(CLAVE_REGEXP), Length(max=16)])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
