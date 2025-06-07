"""
Web Páginas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DateTimeLocalField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from ...lib.safe_string import PATH_REGEXP


class WebPaginaNewForm(FlaskForm):
    """Formulario nuevo WebPagina"""

    clave = StringField(
        "Clave (solo letras mayúsculas y números hasta 16 caracteres)", validators=[DataRequired(), Length(max=16)]
    )
    nombre = StringField("Nombre (solo letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    ruta = StringField("Ruta", validators=[DataRequired(), Length(max=256), Regexp(PATH_REGEXP)])
    guardar = SubmitField("Guardar")


class WebPaginaEditForm(FlaskForm):
    """Formulario editar WebPagina"""

    clave = StringField(
        "Clave (solo letras mayúsculas y números hasta 16 caracteres)", validators=[DataRequired(), Length(max=16)]
    )
    nombre = StringField("Nombre (solo letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    ruta = StringField("Ruta", validators=[DataRequired(), Length(max=256), Regexp(PATH_REGEXP)])
    resumen = TextAreaField("Resumen", validators=[Optional()], render_kw={"rows": 8})
    fecha_modificacion = DateField("Fecha de modificación", validators=[DataRequired()])
    responsable = StringField("Responsable", validators=[Optional(), Length(max=256)])
    etiquetas = StringField("Etiquetas", validators=[Optional(), Length(max=256)])
    vista_previa = StringField("Vista previa", validators=[Optional(), Length(max=256)])
    tiempo_publicar = DateTimeLocalField("Cuándo publicar", validators=[Optional()])
    tiempo_archivar = DateTimeLocalField("Cuándo archivar", validators=[Optional()])
    esta_archivado = BooleanField("Está archivado", validators=[Optional()])
    guardar = SubmitField("Guardar")


class WebPaginaContenidoForm(FlaskForm):
    """Formulario contenido WebPagina"""

    contenido = TextAreaField("Contenido", validators=[DataRequired()], render_kw={"rows": 10})
    guardar = SubmitField("Guardar")
