"""
Pruebas del servicio login_ban

No usan la base de datos: los bloqueos y los intentos se cargan en un repositorio en memoria
a partir de listas de diccionarios, y el reloj está fijo en AHORA para simular el paso del tiempo.

Ejecutar con:

    pytest tests/test_login_ban.py -v
"""

from datetime import datetime, timedelta
from typing import Optional

import pytest

from pjecz_casiopea_flask.config.settings import get_settings
from pjecz_casiopea_flask.services.login_ban import Bloqueo, ConfigBan, Intento, LoginBanService, TipoBan

# Reloj fijo a mediodía, así sumar o restar minutos no cambia de día
AHORA = datetime(2026, 11, 24, 12, 0, 0)

# Reglas de prueba, iguales a las de .env.example. Se dan explícitas para no depender del settings
CONFIG = ConfigBan(max_intentos=5, duracion_minutos=30, max_bloqueos_por_dia=3)

IP_ATACANTE = "45.231.12.4"
IP_OTRA = "189.203.10.25"
EMAIL_COMPROMETIDO = "admin@ejemplo.com"
EMAIL_OTRO = "usuario1@ejemplo.gob.mx"


class RepositorioEnMemoria:
    """Repositorio de prueba que guarda los bloqueos y los intentos en listas"""

    def __init__(self, bloqueos: Optional[list[dict]] = None, intentos: Optional[list[dict]] = None):
        """
        Cada bloqueo es un dict con: tipo ("MINUTOS", "DIA" o "SIEMPRE"), minutos_atras,
        y opcionalmente direccion_ip, email y estatus ("A" o "B").
        Cada intento es un dict con: direccion_ip, email, intentos y minutos_atras.
        """
        self.bloqueos: list[dict] = []
        self.intentos: list[dict] = []
        for datos in bloqueos or []:
            self.bloqueos.append(
                {
                    "id": len(self.bloqueos) + 1,
                    "tipo": TipoBan[datos["tipo"]],
                    "tiempo": AHORA - timedelta(minutes=datos["minutos_atras"]),
                    "direccion_ip": datos.get("direccion_ip"),
                    "email": datos.get("email"),
                    "estatus": datos.get("estatus", "A"),
                }
            )
        for datos in intentos or []:
            self.intentos.append(
                {
                    "id": len(self.intentos) + 1,
                    "direccion_ip": datos["direccion_ip"],
                    "email": datos["email"],
                    "intentos": datos["intentos"],
                    "tiempo": AHORA - timedelta(minutes=datos["minutos_atras"]),
                    "estatus": "A",
                }
            )

    def buscar_bloqueos_activos(self, direccion_ip: str, email: str) -> list[Bloqueo]:
        return [
            self._a_bloqueo(fila)
            for fila in self.bloqueos
            if fila["estatus"] == "A"
            and ((direccion_ip and fila["direccion_ip"] == direccion_ip) or (email and fila["email"] == email))
        ]

    def desactivar_bloqueo(self, bloqueo: Bloqueo) -> None:
        for fila in self.bloqueos:
            if fila["id"] == bloqueo.id:
                fila["estatus"] = "B"

    def crear_bloqueo(self, bloqueo: Bloqueo) -> Bloqueo:
        fila = {
            "id": len(self.bloqueos) + 1,
            "tipo": bloqueo.tipo,
            "tiempo": bloqueo.tiempo,
            "direccion_ip": bloqueo.direccion_ip,
            "email": bloqueo.email,
            "estatus": "A",
        }
        self.bloqueos.append(fila)
        return self._a_bloqueo(fila)

    def contar_bloqueos(self, tipo: TipoBan, direccion_ip: str, email: str, desde: datetime) -> int:
        return sum(
            1
            for fila in self.bloqueos
            if fila["tipo"] == tipo and fila["direccion_ip"] == direccion_ip and fila["email"] == email and fila["tiempo"] >= desde
        )

    def obtener_intento(self, direccion_ip: str, email: str) -> Optional[Intento]:
        for fila in self.intentos:
            if fila["estatus"] == "A" and fila["direccion_ip"] == direccion_ip and fila["email"] == email:
                return Intento(fila["id"], fila["direccion_ip"], fila["email"], fila["intentos"], fila["tiempo"])
        return None

    def guardar_intento(self, intento: Intento) -> Intento:
        if intento.id is None:
            intento.id = len(self.intentos) + 1
            self.intentos.append({"id": intento.id, "estatus": "A"})
        fila = next(f for f in self.intentos if f["id"] == intento.id)
        fila.update(direccion_ip=intento.direccion_ip, email=intento.email, intentos=intento.intentos, tiempo=intento.tiempo)
        return intento

    def desactivar_intento(self, intento: Intento) -> None:
        for fila in self.intentos:
            if fila["id"] == intento.id:
                fila["estatus"] = "B"

    @staticmethod
    def _a_bloqueo(fila: dict) -> Bloqueo:
        return Bloqueo(fila["id"], fila["tipo"], fila["tiempo"], fila["direccion_ip"], fila["email"])


class Reloj:
    """Reloj que se puede adelantar durante una prueba"""

    def __init__(self, inicio: datetime = AHORA):
        self.actual = inicio

    def __call__(self) -> datetime:
        return self.actual

    def adelantar(self, minutos: int) -> None:
        self.actual += timedelta(minutes=minutos)


def crear_servicio(bloqueos=None, intentos=None, reloj=None):
    """Entrega el servicio y su repositorio para poder revisar las tablas después"""
    repositorio = RepositorioEnMemoria(bloqueos, intentos)
    servicio = LoginBanService(repositorio, CONFIG, ahora=reloj or Reloj())
    return servicio, repositorio


@pytest.fixture
def settings_limpio():
    """Vaciar el caché de get_settings antes y después, para que lea las variables de entorno de la prueba"""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_config_ban_carga_valores_de_settings(monkeypatch, settings_limpio):
    """ConfigBan() sin argumentos toma BAN_MAX_ATTEMPTS, BAN_DURATION_MINUTES y BAN_MAX_ATTEMPTS_PER_DAY"""
    monkeypatch.setenv("BAN_MAX_ATTEMPTS", "7")
    monkeypatch.setenv("BAN_DURATION_MINUTES", "15")
    monkeypatch.setenv("BAN_MAX_ATTEMPTS_PER_DAY", "2")
    config = ConfigBan()
    assert config == ConfigBan(max_intentos=7, duracion_minutos=15, max_bloqueos_por_dia=2)
    assert isinstance(config.max_intentos, int)


def test_config_ban_valor_explicito_no_lee_settings(monkeypatch, settings_limpio):
    """Un valor explícito gana sobre settings, los demás se toman de settings"""
    monkeypatch.setenv("BAN_MAX_ATTEMPTS", "7")
    monkeypatch.setenv("BAN_DURATION_MINUTES", "15")
    monkeypatch.setenv("BAN_MAX_ATTEMPTS_PER_DAY", "2")
    config = ConfigBan(max_intentos=3)
    assert config == ConfigBan(max_intentos=3, duracion_minutos=15, max_bloqueos_por_dia=2)


def test_servicio_sin_config_usa_settings(monkeypatch, settings_limpio):
    """Si no se da ConfigBan, el servicio aplica las reglas de settings"""
    monkeypatch.setenv("BAN_MAX_ATTEMPTS", "2")
    monkeypatch.setenv("BAN_DURATION_MINUTES", "30")
    monkeypatch.setenv("BAN_MAX_ATTEMPTS_PER_DAY", "3")
    servicio = LoginBanService(RepositorioEnMemoria(), ahora=Reloj())
    assert not servicio.registrar_intento_fallido(IP_ATACANTE, EMAIL_OTRO).bloqueado
    assert servicio.registrar_intento_fallido(IP_ATACANTE, EMAIL_OTRO).bloqueado


# Escenarios de consulta: ¿puede entrar esta dirección IP con este email?
ESCENARIOS_CONSULTA = [
    {
        "nombre": "ip bloqueada permanentemente, con cualquier email",
        "bloqueos": [{"tipo": "SIEMPRE", "direccion_ip": IP_ATACANTE, "minutos_atras": 60 * 24 * 30}],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_OTRO,
        "bloqueado": True,
        "tipo": TipoBan.SIEMPRE,
    },
    {
        "nombre": "ip bloqueada permanentemente no afecta a otra ip",
        "bloqueos": [{"tipo": "SIEMPRE", "direccion_ip": IP_ATACANTE, "minutos_atras": 60 * 24 * 30}],
        "direccion_ip": IP_OTRA,
        "email": EMAIL_OTRO,
        "bloqueado": False,
        "tipo": None,
    },
    {
        "nombre": "email bloqueado permanentemente, desde cualquier ip",
        "bloqueos": [{"tipo": "SIEMPRE", "email": EMAIL_COMPROMETIDO, "minutos_atras": 60 * 24 * 30}],
        "direccion_ip": IP_OTRA,
        "email": EMAIL_COMPROMETIDO,
        "bloqueado": True,
        "tipo": TipoBan.SIEMPRE,
    },
    {
        "nombre": "email bloqueado se compara sin mayusculas ni espacios",
        "bloqueos": [{"tipo": "SIEMPRE", "email": EMAIL_COMPROMETIDO, "minutos_atras": 5}],
        "direccion_ip": IP_OTRA,
        "email": "  ADMIN@Ejemplo.com ",
        "bloqueado": True,
        "tipo": TipoBan.SIEMPRE,
    },
    {
        "nombre": "bloqueo dado de baja no bloquea",
        "bloqueos": [{"tipo": "SIEMPRE", "direccion_ip": IP_ATACANTE, "minutos_atras": 5, "estatus": "B"}],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_OTRO,
        "bloqueado": False,
        "tipo": None,
    },
    {
        "nombre": "bloqueo por minutos sin superar el tiempo sigue bloqueado",
        "bloqueos": [{"tipo": "MINUTOS", "direccion_ip": IP_ATACANTE, "minutos_atras": 29}],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_OTRO,
        "bloqueado": True,
        "tipo": TipoBan.MINUTOS,
    },
    {
        "nombre": "bloqueo por minutos superando el tiempo ya puede entrar",
        "bloqueos": [{"tipo": "MINUTOS", "direccion_ip": IP_ATACANTE, "minutos_atras": 31}],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_OTRO,
        "bloqueado": False,
        "tipo": None,
    },
    {
        "nombre": "bloqueo por dia, el mismo dia sigue bloqueado",
        "bloqueos": [{"tipo": "DIA", "email": EMAIL_COMPROMETIDO, "minutos_atras": 60 * 11}],
        "direccion_ip": IP_OTRA,
        "email": EMAIL_COMPROMETIDO,
        "bloqueado": True,
        "tipo": TipoBan.DIA,
    },
    {
        "nombre": "bloqueo por dia, al dia siguiente ya puede entrar",
        "bloqueos": [{"tipo": "DIA", "email": EMAIL_COMPROMETIDO, "minutos_atras": 60 * 13}],
        "direccion_ip": IP_OTRA,
        "email": EMAIL_COMPROMETIDO,
        "bloqueado": False,
        "tipo": None,
    },
    {
        "nombre": "con varios bloqueos se informa el mas severo",
        "bloqueos": [
            {"tipo": "MINUTOS", "direccion_ip": IP_ATACANTE, "minutos_atras": 5},
            {"tipo": "SIEMPRE", "email": EMAIL_COMPROMETIDO, "minutos_atras": 5},
        ],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_COMPROMETIDO,
        "bloqueado": True,
        "tipo": TipoBan.SIEMPRE,
    },
    {
        "nombre": "email bloqueado no afecta a otro email desde la misma ip",
        "bloqueos": [{"tipo": "SIEMPRE", "email": EMAIL_COMPROMETIDO, "minutos_atras": 5}],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_OTRO,
        "bloqueado": False,
        "tipo": None,
    },
    {
        "nombre": "ip y email bloqueados juntos, coinciden los dos",
        "bloqueos": [{"tipo": "SIEMPRE", "direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "minutos_atras": 5}],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_COMPROMETIDO,
        "bloqueado": True,
        "tipo": TipoBan.SIEMPRE,
    },
    {
        "nombre": "ip y email bloqueados juntos, misma ip con otro email puede entrar",
        "bloqueos": [{"tipo": "SIEMPRE", "direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "minutos_atras": 5}],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_OTRO,
        "bloqueado": False,
        "tipo": None,
    },
    {
        "nombre": "ip y email bloqueados juntos, mismo email desde otra ip puede entrar",
        "bloqueos": [{"tipo": "SIEMPRE", "direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "minutos_atras": 5}],
        "direccion_ip": IP_OTRA,
        "email": EMAIL_COMPROMETIDO,
        "bloqueado": False,
        "tipo": None,
    },
    {
        "nombre": "ip y email bloqueados juntos, email se compara sin mayusculas ni espacios",
        "bloqueos": [{"tipo": "SIEMPRE", "direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "minutos_atras": 5}],
        "direccion_ip": IP_ATACANTE,
        "email": "  ADMIN@Ejemplo.com ",
        "bloqueado": True,
        "tipo": TipoBan.SIEMPRE,
    },
    {
        "nombre": "bloqueo de la pareja no impide que aplique el bloqueo solo por ip",
        "bloqueos": [
            {"tipo": "SIEMPRE", "direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "minutos_atras": 5},
            {"tipo": "MINUTOS", "direccion_ip": IP_ATACANTE, "minutos_atras": 5},
        ],
        "direccion_ip": IP_ATACANTE,
        "email": EMAIL_OTRO,
        "bloqueado": True,
        "tipo": TipoBan.MINUTOS,
    },
]


@pytest.mark.parametrize("escenario", ESCENARIOS_CONSULTA, ids=[e["nombre"] for e in ESCENARIOS_CONSULTA])
def test_esta_bloqueado(escenario):
    """Consultar si una pareja (dirección IP, email) puede entrar"""
    servicio, _ = crear_servicio(bloqueos=escenario["bloqueos"])
    resultado = servicio.esta_bloqueado(escenario["direccion_ip"], escenario["email"])
    assert resultado.bloqueado is escenario["bloqueado"]
    assert resultado.tipo == escenario["tipo"]


def test_bloqueo_por_minutos_vigente_informa_hasta_cuando():
    """Sin superar el tiempo, el resultado dice cuándo podrá volver a intentar"""
    servicio, _ = crear_servicio(bloqueos=[{"tipo": "MINUTOS", "direccion_ip": IP_ATACANTE, "minutos_atras": 10}])
    resultado = servicio.esta_bloqueado(IP_ATACANTE, EMAIL_OTRO)
    assert resultado.bloqueado
    assert resultado.hasta == AHORA + timedelta(minutes=20)


def test_bloqueo_por_minutos_caducado_se_da_de_baja():
    """Superando el tiempo, el bloqueo pasa a estatus B en la tabla"""
    servicio, repositorio = crear_servicio(bloqueos=[{"tipo": "MINUTOS", "direccion_ip": IP_ATACANTE, "minutos_atras": 31}])
    assert not servicio.esta_bloqueado(IP_ATACANTE, EMAIL_OTRO).bloqueado
    assert repositorio.bloqueos[0]["estatus"] == "B"


def test_bloqueo_por_minutos_con_el_paso_del_tiempo():
    """El mismo bloqueo, antes y después de cumplirse los minutos"""
    reloj = Reloj()
    servicio, _ = crear_servicio(bloqueos=[{"tipo": "MINUTOS", "direccion_ip": IP_ATACANTE, "minutos_atras": 0}], reloj=reloj)
    reloj.adelantar(CONFIG.duracion_minutos - 1)
    assert servicio.esta_bloqueado(IP_ATACANTE, EMAIL_OTRO).bloqueado
    reloj.adelantar(1)
    assert not servicio.esta_bloqueado(IP_ATACANTE, EMAIL_OTRO).bloqueado


def test_consultar_no_cuenta_como_intento():
    """Preguntar si está bloqueado no debe sumar intentos"""
    servicio, repositorio = crear_servicio()
    for _ in range(CONFIG.max_intentos + 1):
        servicio.esta_bloqueado(IP_ATACANTE, EMAIL_OTRO)
    assert repositorio.intentos == []
    assert repositorio.bloqueos == []


def test_superar_maximo_de_intentos_bloquea_por_minutos():
    """Al llegar al máximo de intentos se agrega un bloqueo por MINUTOS a la tabla de baneo"""
    servicio, repositorio = crear_servicio()
    # Los primeros intentos fallidos solo suman
    for numero in range(1, CONFIG.max_intentos):
        resultado = servicio.registrar_intento_fallido(IP_ATACANTE, EMAIL_COMPROMETIDO)
        assert not resultado.bloqueado
        assert resultado.intentos == numero
    assert repositorio.bloqueos == []
    # El que llega al máximo bloquea
    resultado = servicio.registrar_intento_fallido(IP_ATACANTE, EMAIL_COMPROMETIDO)
    assert resultado.bloqueado
    assert resultado.tipo == TipoBan.MINUTOS
    assert resultado.intentos == CONFIG.max_intentos
    assert resultado.hasta == AHORA + timedelta(minutes=CONFIG.duracion_minutos)
    # Revisar que pasó a la tabla de baneo
    assert len(repositorio.bloqueos) == 1
    bloqueo = repositorio.bloqueos[0]
    assert bloqueo["tipo"] == TipoBan.MINUTOS
    assert bloqueo["direccion_ip"] == IP_ATACANTE
    assert bloqueo["email"] == EMAIL_COMPROMETIDO
    assert bloqueo["estatus"] == "A"
    assert bloqueo["tiempo"] == AHORA
    # El contador vuelve a cero y la consulta ya lo reporta bloqueado
    assert repositorio.intentos[0]["intentos"] == 0
    assert servicio.esta_bloqueado(IP_ATACANTE, EMAIL_COMPROMETIDO).bloqueado
    # El bloqueo automático es de la pareja: la misma IP con otro email, o el email desde otra IP, pueden entrar
    assert not servicio.esta_bloqueado(IP_ATACANTE, EMAIL_OTRO).bloqueado
    assert not servicio.esta_bloqueado(IP_OTRA, EMAIL_COMPROMETIDO).bloqueado


def test_superar_maximo_de_intentos_con_contador_previo():
    """Con un contador ya cargado, el siguiente intento fallido es el que bloquea"""
    servicio, repositorio = crear_servicio(
        intentos=[{"direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "intentos": CONFIG.max_intentos - 1, "minutos_atras": 2}]
    )
    resultado = servicio.registrar_intento_fallido(IP_ATACANTE, EMAIL_COMPROMETIDO)
    assert resultado.bloqueado
    assert resultado.tipo == TipoBan.MINUTOS
    assert len(repositorio.bloqueos) == 1


def test_contador_de_otro_dia_empieza_de_nuevo():
    """Los intentos de un día anterior no cuentan para el máximo"""
    servicio, repositorio = crear_servicio(
        intentos=[{"direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "intentos": CONFIG.max_intentos - 1, "minutos_atras": 60 * 24}]
    )
    resultado = servicio.registrar_intento_fallido(IP_ATACANTE, EMAIL_COMPROMETIDO)
    assert not resultado.bloqueado
    assert resultado.intentos == 1
    assert repositorio.bloqueos == []


def test_acceso_exitoso_da_de_baja_el_contador():
    """Después de entrar con éxito, el contador pasa a estatus B como historial y conserva sus intentos"""
    servicio, repositorio = crear_servicio(
        intentos=[{"direccion_ip": IP_OTRA, "email": EMAIL_OTRO, "intentos": CONFIG.max_intentos - 1, "minutos_atras": 1}]
    )
    servicio.registrar_acceso_exitoso(IP_OTRA, EMAIL_OTRO)
    assert repositorio.intentos[0]["estatus"] == "B"
    assert repositorio.intentos[0]["intentos"] == CONFIG.max_intentos - 1


def test_despues_de_acceso_exitoso_comienza_un_registro_nuevo():
    """Al volver a fallar tras un acceso exitoso, se crea otro registro de intentos desde uno"""
    servicio, repositorio = crear_servicio(
        intentos=[{"direccion_ip": IP_OTRA, "email": EMAIL_OTRO, "intentos": CONFIG.max_intentos - 1, "minutos_atras": 1}]
    )
    servicio.registrar_acceso_exitoso(IP_OTRA, EMAIL_OTRO)
    resultado = servicio.registrar_intento_fallido(IP_OTRA, EMAIL_OTRO)
    assert not resultado.bloqueado
    assert resultado.intentos == 1
    assert [(fila["estatus"], fila["intentos"]) for fila in repositorio.intentos] == [("B", CONFIG.max_intentos - 1), ("A", 1)]


def test_acceso_exitoso_sin_intentos_no_crea_registro():
    """Si la pareja no tenía intentos fallidos, entrar con éxito no agrega nada a la tabla"""
    servicio, repositorio = crear_servicio()
    servicio.registrar_acceso_exitoso(IP_OTRA, EMAIL_OTRO)
    assert repositorio.intentos == []


def test_acceso_exitoso_solo_da_de_baja_su_pareja():
    """Los contadores de otras parejas siguen activos"""
    servicio, repositorio = crear_servicio(
        intentos=[
            {"direccion_ip": IP_OTRA, "email": EMAIL_OTRO, "intentos": 2, "minutos_atras": 1},
            {"direccion_ip": IP_ATACANTE, "email": EMAIL_OTRO, "intentos": 3, "minutos_atras": 1},
        ]
    )
    servicio.registrar_acceso_exitoso(IP_OTRA, EMAIL_OTRO)
    assert [fila["estatus"] for fila in repositorio.intentos] == ["B", "A"]


# Escenarios del máximo de bloqueos por minutos al día
ESCENARIOS_POR_DIA = [
    {
        "nombre": "sobrepasa el máximo por día y se bloquea para siempre",
        "bloqueos_previos_minutos_atras": [60 * 3, 60 * 2, 60],  # Tres bloqueos hoy, ya caducados
        "tipo": TipoBan.SIEMPRE,
    },
    {
        "nombre": "sin llegar al máximo por día solo se bloquea por minutos",
        "bloqueos_previos_minutos_atras": [60 * 2, 60],
        "tipo": TipoBan.MINUTOS,
    },
    {
        "nombre": "los bloqueos de ayer no cuentan para el máximo por día",
        "bloqueos_previos_minutos_atras": [60 * 24, 60 * 23, 60 * 13],
        "tipo": TipoBan.MINUTOS,
    },
]


@pytest.mark.parametrize("escenario", ESCENARIOS_POR_DIA, ids=[e["nombre"] for e in ESCENARIOS_POR_DIA])
def test_maximo_de_bloqueos_por_dia(escenario):
    """Al llegar otra vez al máximo de intentos, el tipo de bloqueo depende de los bloqueos por minutos del día"""
    bloqueos = [
        {"tipo": "MINUTOS", "direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "minutos_atras": minutos, "estatus": "B"}
        for minutos in escenario["bloqueos_previos_minutos_atras"]
    ]
    intentos = [{"direccion_ip": IP_ATACANTE, "email": EMAIL_COMPROMETIDO, "intentos": CONFIG.max_intentos - 1, "minutos_atras": 1}]
    servicio, repositorio = crear_servicio(bloqueos=bloqueos, intentos=intentos)
    resultado = servicio.registrar_intento_fallido(IP_ATACANTE, EMAIL_COMPROMETIDO)
    assert resultado.bloqueado
    assert resultado.tipo == escenario["tipo"]
    # Revisar que el nuevo bloqueo pasó a la tabla de baneo
    nuevo = repositorio.bloqueos[-1]
    assert len(repositorio.bloqueos) == len(bloqueos) + 1
    assert nuevo["tipo"] == escenario["tipo"]
    assert nuevo["direccion_ip"] == IP_ATACANTE
    assert nuevo["email"] == EMAIL_COMPROMETIDO
    assert nuevo["estatus"] == "A"


def test_ataque_completo_de_un_dia():
    """Simula un día de ataque: tres rondas bloqueadas por minutos y la cuarta para siempre"""
    reloj = Reloj(AHORA.replace(hour=8))
    servicio, repositorio = crear_servicio(reloj=reloj)
    for ronda in range(1, CONFIG.max_bloqueos_por_dia + 2):
        # Espera a que caduque el bloqueo anterior
        assert not servicio.esta_bloqueado(IP_ATACANTE, EMAIL_COMPROMETIDO).bloqueado
        for _ in range(CONFIG.max_intentos):
            resultado = servicio.registrar_intento_fallido(IP_ATACANTE, EMAIL_COMPROMETIDO)
        esperado = TipoBan.SIEMPRE if ronda > CONFIG.max_bloqueos_por_dia else TipoBan.MINUTOS
        assert resultado.tipo == esperado
        reloj.adelantar(CONFIG.duracion_minutos)
    # Tres bloqueos por minutos ya caducados y uno para siempre vigente
    tipos = [(fila["tipo"], fila["estatus"]) for fila in repositorio.bloqueos]
    assert tipos == [(TipoBan.MINUTOS, "B")] * CONFIG.max_bloqueos_por_dia + [(TipoBan.SIEMPRE, "A")]
    assert servicio.esta_bloqueado(IP_ATACANTE, EMAIL_COMPROMETIDO).tipo == TipoBan.SIEMPRE
