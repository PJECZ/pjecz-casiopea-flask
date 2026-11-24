"""
Pruebas de la caducidad de la sesión

Usan una aplicación Flask mínima (sin base de datos) para tener una sesión real.

Ejecutar con:

    pytest tests/test_sesion_caducidad.py -v
"""

import pytest
from flask import Flask, session

from pjecz_casiopea_flask.lib.sesion_caducidad import CLAVE_INICIO_SESION, marcar_inicio_sesion, sesion_caducada

INICIO = 1_800_000_000.0  # Hora fija del login, en segundos desde epoch
HORA = 60 * 60


@pytest.fixture
def app():
    aplicacion = Flask(__name__)
    aplicacion.secret_key = "prueba"
    return aplicacion


def test_marcar_inicio_sesion_guarda_la_hora(app):
    with app.test_request_context():
        marcar_inicio_sesion(INICIO)
        assert session[CLAVE_INICIO_SESION] == INICIO


@pytest.mark.parametrize(
    "horas_despues, caducada",
    [(0, False), (23, False), (23.99, False), (24, True), (30, True)],
)
def test_sesion_caduca_a_las_24_horas_del_login(app, horas_despues, caducada):
    with app.test_request_context():
        marcar_inicio_sesion(INICIO)
        assert sesion_caducada(24, ahora=INICIO + horas_despues * HORA) is caducada


def test_sesion_sin_hora_de_inicio_esta_caducada(app):
    """Las sesiones abiertas antes de esta regla no tienen hora de inicio y se cierran"""
    with app.test_request_context():
        assert sesion_caducada(24, ahora=INICIO)


def test_hora_de_inicio_invalida_esta_caducada(app):
    with app.test_request_context():
        session[CLAVE_INICIO_SESION] = "no es una hora"
        assert sesion_caducada(24, ahora=INICIO)


def test_duracion_configurable(app):
    with app.test_request_context():
        marcar_inicio_sesion(INICIO)
        assert not sesion_caducada(8, ahora=INICIO + 7 * HORA)
        assert sesion_caducada(8, ahora=INICIO + 8 * HORA)
