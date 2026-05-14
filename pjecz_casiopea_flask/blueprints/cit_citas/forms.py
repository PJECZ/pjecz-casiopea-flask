"""
Citas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ReadOnly


class CitaAsistenciaForm(FlaskForm):
    """Formulario Asistencia a Cita"""

    id = StringField("ID")
    cliente_nombre = StringField("Cliente")
    codigo_asistencia = StringField("Código de Asistencia", validators=[DataRequired()])
    guardar = SubmitField("Guardar")