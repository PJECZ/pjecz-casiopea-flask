"""
Caducidad de la sesión

La sesión dura un tiempo fijo a partir del login (por defecto 24 horas), sin importar la actividad.
- Al hacer login se guarda en la sesión la hora de inicio con `marcar_inicio_sesion()`.
- En cada petición `sesion_caducada()` revisa si ya pasó la duración, o si falta la hora de inicio.
"""

import time
from typing import Optional

from flask import session

CLAVE_INICIO_SESION = "inicio_sesion"


def marcar_inicio_sesion(ahora: Optional[float] = None) -> None:
    """Guardar en la sesión la hora del login (segundos desde epoch)"""
    session[CLAVE_INICIO_SESION] = time.time() if ahora is None else ahora


def sesion_caducada(duracion_horas: int, ahora: Optional[float] = None) -> bool:
    """Saber si la sesión ya caducó. Sin hora de inicio (sesión anterior a esta regla) también se considera caducada"""
    inicio = session.get(CLAVE_INICIO_SESION)
    if not isinstance(inicio, (int, float)):
        return True
    ahora = time.time() if ahora is None else ahora
    return ahora - inicio >= duracion_horas * 60 * 60
