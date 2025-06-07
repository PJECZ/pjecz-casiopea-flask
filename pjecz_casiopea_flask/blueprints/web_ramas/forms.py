"""
Web Ramas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from ...lib.safe_string import PATH_REGEXP


class WebRamaNewForm(FlaskForm):
    """Formulario nueva WebRama"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    nombre = StringField("Nombre (solo letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    ruta = StringField("Ruta", validators=[DataRequired(), Length(max=256), Regexp(PATH_REGEXP)])
    guardar = SubmitField("Guardar")


class WebRamaEditForm(FlaskForm):
    """Formulario editar WebRama"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    nombre = StringField("Nombre (solo letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    ruta = StringField("Ruta", validators=[DataRequired(), Length(max=256), Regexp(PATH_REGEXP)])
    esta_archivado = BooleanField("Está archivado", validators=[Optional()], default=False)
    guardar = SubmitField("Guardar")
