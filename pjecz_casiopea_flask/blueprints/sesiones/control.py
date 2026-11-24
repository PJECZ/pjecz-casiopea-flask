"""
Sesiones, control de la sesión del usuario

Cada usuario tiene un solo registro en `sesiones` (su id es el del usuario), así que solo puede
tener una sesión a la vez: al entrar desde otro navegador cambia el identificador y la anterior deja de valer.

- abrir_sesion(usuario): al hacer login, crea o reutiliza el registro y lo marca como activo.
- sesion_vigente(usuario): en cada petición, revisa que el registro siga activo y sea de esta sesión.
- cerrar_sesion(usuario): al salir o caducar, marca el registro como inactivo.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from flask import request, session

from .models import Sesion

CLAVE_IDENTIFICADOR = "sesion_identificador"

# Para no escribir en cada petición, el último acceso se actualiza cuando pasó al menos este tiempo
INTERVALO_ULTIMO_ACCESO = timedelta(minutes=1)


def abrir_sesion(usuario, ahora: Optional[datetime] = None) -> Sesion:
    """Crear o reutilizar el registro del usuario con un identificador nuevo, y guardarlo en la cookie de sesión"""
    ahora = ahora or datetime.now()
    sesion = Sesion.query.get(usuario.id)
    if sesion is None:
        sesion = Sesion(id=usuario.id)
    sesion.activa = True
    sesion.identificador = secrets.token_urlsafe(32)
    sesion.direccion_ip = (request.remote_addr or "")[:64]
    sesion.navegador = (request.user_agent.string or "")[:256]
    sesion.inicio = ahora
    sesion.ultimo_acceso = ahora
    sesion.save()
    session[CLAVE_IDENTIFICADOR] = sesion.identificador
    return sesion


def _es_de_esta_sesion(sesion: Optional[Sesion]) -> bool:
    """El registro existe y su identificador es el de la cookie"""
    identificador = session.get(CLAVE_IDENTIFICADOR)
    return sesion is not None and identificador is not None and secrets.compare_digest(sesion.identificador, identificador)


def sesion_vigente(usuario, ahora: Optional[datetime] = None) -> bool:
    """Saber si la sesión sigue activa y es la de este navegador, y actualizar su último acceso"""
    ahora = ahora or datetime.now()
    sesion = Sesion.query.get(usuario.id)
    if not _es_de_esta_sesion(sesion) or not sesion.activa:
        return False
    if ahora - sesion.ultimo_acceso >= INTERVALO_ULTIMO_ACCESO:
        sesion.ultimo_acceso = ahora
        sesion.save()
    return True


def cerrar_sesion(usuario) -> None:
    """Marcar como inactivo el registro, solo si es el de esta sesión"""
    sesion = Sesion.query.get(usuario.id)
    if _es_de_esta_sesion(sesion) and sesion.activa:
        sesion.activa = False
        sesion.save()
    session.pop(CLAVE_IDENTIFICADOR, None)
