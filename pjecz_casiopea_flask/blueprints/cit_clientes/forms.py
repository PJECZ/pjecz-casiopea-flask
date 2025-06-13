"""
Cit Clientes, formularios
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, Regexp

from pjecz_casiopea_flask.lib.pwgen import PASSWORD_REGEXP


class CitClienteForm(FlaskForm):
    """Formulario Cit Dia Inhábil"""

    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_primero = StringField("Apellido primero", validators=[DataRequired(), Length(max=256)])
    apellido_segundo = StringField("Apellido segundo", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP (18 caracteres)", validators=[DataRequired(), Length(min=18, max=18)])
    telefono = StringField("Teléfono (10 números)", validators=[DataRequired(), Length(min=10, max=10)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email()])
    contrasena = PasswordField(
        "Contraseña (8 a 24 caracteres: mayúsculas, minúsculas y números)", validators=[Optional(), Regexp(PASSWORD_REGEXP)]
    )
    limite_citas_pendientes = IntegerField(
        "Límite de citas pendientes (1 a 100)", validators=[DataRequired(), NumberRange(1, 100)]
    )
    guardar = SubmitField("Guardar")
