"""
CLI Commands Cit Citas
"""

import random
from datetime import datetime, time, timedelta

from faker import Faker
from rich.console import Console
from rich.progress import Progress
from sqlalchemy.sql import func
from typer import Typer

from pjecz_casiopea_flask.blueprints.cit_citas.models import CitCita, database
from pjecz_casiopea_flask.blueprints.cit_clientes.models import CitCliente
from pjecz_casiopea_flask.blueprints.cit_oficinas_servicios.models import CitOficinaServicio
from pjecz_casiopea_flask.blueprints.cit_servicios.models import CitServicio
from pjecz_casiopea_flask.blueprints.oficinas.models import Oficina
from pjecz_casiopea_flask.main import app

app.app_context().push()

cit_citas = Typer()


@cit_citas.command()
def agregar_falsos(maximo: int = 10, desde: str = "", hasta: str = ""):
    """Agregar citas con datos falsos"""
    console = Console()
