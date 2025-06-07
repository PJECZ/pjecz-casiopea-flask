"""
Web Archivos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class WebArchivoForm(FlaskForm):
    """Formulario WebArchivo"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    archivo = StringField("Archivo", validators=[DataRequired(), Length(max=256)])
    url = StringField("URL", validators=[DataRequired(), Length(max=256)])
    esta_archivado = BooleanField("Está archivado", validators=[Optional()], default=False)
    guardar = SubmitField("Guardar")
