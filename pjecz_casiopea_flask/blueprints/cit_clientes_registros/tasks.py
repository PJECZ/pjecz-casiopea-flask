"""
Cit Clientes Registros, tareas en el fondo
"""

import logging
import os
from datetime import datetime

import pytz
import sendgrid
from jinja2 import Environment, FileSystemLoader
from sendgrid.helpers.mail import Content, Email, Mail, To

from pjecz_casiopea_flask.blueprints.cit_clientes_registros.models import CitClienteRegistro
from pjecz_casiopea_flask.config.extensions import database
from pjecz_casiopea_flask.lib.tasks import set_task_error, set_task_progress
from pjecz_casiopea_flask.main import app

app.app_context().push()
database.app = app


def enviar():
    """Enviar mensaje via email con un URL para confirmar su registro"""


def reenviar():
    """Reenviar mensajes via email con un URL a quienes deben confirmar su registro"""


def lanzar_enviar():
    """Lanzar la tarea en el fondo para enviar"""


def lanzar_reenviar():
    """Lanzar la tarea en el fondo para reenviar"""
