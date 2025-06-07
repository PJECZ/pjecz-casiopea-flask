"""
Web Archivos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class WebArchivoNewForm(FlaskForm):
    """Formulario WebArchivo"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    nombre = StringField("Nombre (solo letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    archivo = StringField("Archivo", validators=[DataRequired(), Length(max=256)])
    url = StringField("URL", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class WebArchivoEditForm(FlaskForm):
    """Formulario WebArchivo"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    nombre = StringField("Nombre (solo letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    archivo = StringField("Archivo", validators=[DataRequired(), Length(max=256)])
    url = StringField("URL", validators=[DataRequired(), Length(max=256)])
    esta_archivado = BooleanField("Está archivado", validators=[Optional()], default=False)
    guardar = SubmitField("Guardar")
