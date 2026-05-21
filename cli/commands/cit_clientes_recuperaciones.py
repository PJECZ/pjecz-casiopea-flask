"""
CLI Commands Cit Clientes Recuperaciones
"""
from datetime import datetime, timedelta

from rich.console import Console
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from typer import Typer

from pjecz_casiopea_flask.blueprints.cit_clientes_recuperaciones.models import CitClienteRecuperacion
from pjecz_casiopea_flask.lib.safe_string import safe_email, safe_string
from pjecz_casiopea_flask.main import app

app.app_context().push()

cit_clientes_recuperaciones = Typer()


@cit_clientes_recuperaciones.command()
def eliminar():
    """Eliminar recuperaciones"""
    console = Console()
    console.print("Eliminar recuperaciones que NO fueron realizadas")

    # Consultar recuperaciones cuyo estatus sea "A' y con el booleano ya_recuperado en False
    cit_clientes_recuperaciones = CitClienteRecuperacion.query.filter_by(estatus="A").filter_by(ya_recuperado=False).all()

    # Si no hay recuperaciones que eliminar, mostrar mensaje y salir
    if not cit_clientes_recuperaciones:
        console.print("No hay recuperaciones que eliminar")
        return

    # Eliminar recuperaciones
    contador = 0
    console.print("Eliminando: ", nl=False)
    for cit_cliente_recuperacion in cit_clientes_recuperaciones:
        cit_cliente_recuperacion.delete()
        contador += 1
        console.print(".", nl=False)
    console.print()

    # Mensaje final
    console.print(f"Se eliminaron {contador} recuperaciones")