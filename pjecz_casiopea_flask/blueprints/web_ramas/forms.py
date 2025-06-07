"""
Web Ramas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from ...lib.safe_string import DIRECTORIO_REGEXP


class WebRamaNewForm(FlaskForm):
    """Formulario nueva WebRama"""

    clave = StringField(
        "Clave (solo letras mayúsculas y números hasta 8 caracteres)", validators=[DataRequired(), Length(max=8)]
    )
    nombre = StringField("Nombre (solo letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    unidad_compartida = StringField(
        "Unidad compartida (igual que en Google Drive)", validators=[DataRequired(), Length(max=64)]
    )
    directorio = StringField(
        "Directorio (letras minúsculas, números y guiones)",
        validators=[DataRequired(), Length(max=64), Regexp(DIRECTORIO_REGEXP)],
    )
    guardar = SubmitField("Guardar")


class WebRamaEditForm(FlaskForm):
    """Formulario editar WebRama"""

    clave = StringField(
        "Clave (solo letras mayúsculas y números hasta 8 caracteres)", validators=[DataRequired(), Length(max=8)]
    )
    nombre = StringField("Nombre (solo letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    unidad_compartida = StringField(
        "Unidad compartida (igual que en Google Drive)", validators=[DataRequired(), Length(max=64)]
    )
    directorio = StringField(
        "Directorio (letras minúsculas, números y guiones)",
        validators=[DataRequired(), Length(max=64), Regexp(DIRECTORIO_REGEXP)],
    )
    esta_archivado = BooleanField("Está archivado", validators=[Optional()])
    guardar = SubmitField("Guardar")
