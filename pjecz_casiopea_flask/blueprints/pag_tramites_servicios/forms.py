"""
Pag Trámites Servicios, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class PagTramiteServicioForm(FlaskForm):
    """Formulario PagTramiteServicio"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    costo = DecimalField("Costo", validators=[DataRequired(), NumberRange(min=0)], places=2)
    url = StringField("URL en pjecz.gob.mx", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")
