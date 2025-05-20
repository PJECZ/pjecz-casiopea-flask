"""
Alimentar Usuarios-Roles
"""

import csv
import sys
from pathlib import Path

import click

from pjecz_casiopea_flask.blueprints.roles.models import Rol
from pjecz_casiopea_flask.blueprints.usuarios.models import Usuario
from pjecz_casiopea_flask.blueprints.usuarios_roles.models import UsuarioRol
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_email, safe_string

USUARIOS_ROLES_CSV = "seed/usuarios_roles.csv"


def alimentar_usuarios_roles():
    """Alimentar Usuarios-Roles"""
    ruta = Path(USUARIOS_ROLES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando usuarios-roles: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            email = safe_email(row.get("email"))
            usuario = Usuario.query.filter(Usuario.email == email).first()
            if usuario is None:
                click.echo(click.style(f"  AVISO: usuario {email} no existe", fg="red"))
                sys.exit(1)
            for rol_nombre in row.get("roles").split(","):
                nombre = safe_string(rol_nombre)
                rol = Rol.query.filter(Rol.nombre == nombre).first()
                if rol is None:
                    click.echo(click.style(f"  AVISO: rol {nombre} no existe", fg="red"))
                    sys.exit(1)
                UsuarioRol(
                    usuario=usuario,
                    rol=rol,
                    descripcion=f"{usuario.email} en {rol.nombre}",
                ).save()
                contador += 1
                click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} usuarios-roles alimentados.", fg="green"))
