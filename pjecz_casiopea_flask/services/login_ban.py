"""
Servicio para bannear ataques de login

Reglas:
- Si la dirección IP o el email tienen un bloqueo activo y vigente, no se permite el acceso.
    - SIEMPRE: no caduca.
    - DIA: vigente hasta las 00:00 del día siguiente al bloqueo.
    - MINUTOS: vigente durante `duracion_minutos` a partir del bloqueo.
    - Un bloqueo que ya no está vigente se desactiva (estatus B) al consultarlo.
- Cada intento fallido suma uno al contador de la pareja (dirección IP, email).
    - El contador vuelve a cero al cambiar de día, al bloquear y en un acceso exitoso.
- Al llegar a `max_intentos` se bloquea la pareja (dirección IP, email) por MINUTOS.
    - Si ese mismo día la pareja ya tuvo `max_bloqueos_por_dia` bloqueos por MINUTOS, se bloquea para SIEMPRE.

El servicio no conoce los modelos de SQLAlchemy: trabaja con un repositorio (RepositorioBan).
- En la aplicación se usa RepositorioBanSQLAlchemy, que guarda en las tablas `ban_bloqueados` y `ban_intentos`.
- En las pruebas se puede usar un repositorio en memoria alimentado con listas de diccionarios.

Uso en la vista del login:

    servicio = LoginBanService.desde_settings()
    resultado = servicio.esta_bloqueado(direccion_ip, email)
    if resultado.bloqueado:
        ...  # Rechazar el acceso
    if credenciales_incorrectas:
        resultado = servicio.registrar_intento_fallido(direccion_ip, email)
    else:
        servicio.registrar_acceso_exitoso(direccion_ip, email)
"""

import enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Optional, Protocol


class TipoBan(enum.IntEnum):
    """Tipos de ban, los valores son los id de la tabla `ban_tipos`"""

    MINUTOS = 1  # BAN_MINUTOS
    DIA = 2  # BAN_DIA
    SIEMPRE = 3  # BAN_SIEMPRE


def _valor_de_settings(nombre: str) -> int:
    """Leer una variable de baneo de settings como entero"""
    from ..config.settings import get_settings  # pylint: disable=import-outside-toplevel

    return int(getattr(get_settings(), nombre))


@dataclass
class ConfigBan:
    """
    Reglas de baneo

    ConfigBan() toma los valores de settings (variables de entorno).
    Se pueden dar valores explícitos, por ejemplo en las pruebas: ConfigBan(max_intentos=3)
    """

    # Intentos fallidos antes de bloquear por minutos
    max_intentos: int = field(default_factory=lambda: _valor_de_settings("BAN_MAX_ATTEMPTS"))
    # Duración del bloqueo por minutos
    duracion_minutos: int = field(default_factory=lambda: _valor_de_settings("BAN_DURATION_MINUTES"))
    # Bloqueos por minutos permitidos al día, al sobrepasarlos se bloquea para siempre
    max_bloqueos_por_dia: int = field(default_factory=lambda: _valor_de_settings("BAN_MAX_ATTEMPTS_PER_DAY"))


@dataclass
class Bloqueo:
    """Un registro de la lista de castigo, sin depender del modelo BanBloqueado"""

    id: Optional[int]
    tipo: TipoBan
    tiempo: datetime  # Fecha y hora en que se aplicó el bloqueo
    direccion_ip: Optional[str] = None
    email: Optional[str] = None


@dataclass
class Intento:
    """El contador de intentos fallidos de una pareja (dirección IP, email), sin depender del modelo BanIntento"""

    id: Optional[int]
    direccion_ip: str
    email: str
    intentos: int = 0
    tiempo: Optional[datetime] = None  # Fecha y hora del último intento


@dataclass
class ResultadoBan:
    """Respuesta del servicio"""

    bloqueado: bool
    tipo: Optional[TipoBan] = None
    hasta: Optional[datetime] = None  # None con SIEMPRE o cuando no está bloqueado
    intentos: int = 0  # Intentos fallidos acumulados de la pareja (dirección IP, email)


class RepositorioBan(Protocol):
    """Lo que el servicio necesita para leer y guardar los bloqueos y los intentos"""

    def buscar_bloqueos_activos(self, direccion_ip: str, email: str) -> list[Bloqueo]:
        """Bloqueos activos cuya dirección IP sea `direccion_ip` o cuyo email sea `email`"""

    def desactivar_bloqueo(self, bloqueo: Bloqueo) -> None:
        """Dar de baja un bloqueo que ya no está vigente"""

    def crear_bloqueo(self, bloqueo: Bloqueo) -> Bloqueo:
        """Agregar un bloqueo a la lista de castigo y entregarlo con su id"""

    def contar_bloqueos(self, tipo: TipoBan, direccion_ip: str, email: str, desde: datetime) -> int:
        """Contar los bloqueos de `tipo` de la pareja exacta desde `desde`, activos o ya dados de baja"""

    def obtener_intento(self, direccion_ip: str, email: str) -> Optional[Intento]:
        """El contador activo de la pareja exacta (dirección IP, email), o None si no existe"""

    def guardar_intento(self, intento: Intento) -> Intento:
        """Crear o actualizar el contador y entregarlo con su id"""


class LoginBanService:
    """Servicio para bannear ataques de login"""

    def __init__(
        self,
        repositorio: RepositorioBan,
        config: Optional[ConfigBan] = None,
        ahora: Callable[[], datetime] = datetime.now,
    ):
        self._repositorio = repositorio
        self._config = config if config is not None else ConfigBan()  # Sin config, se toma de settings
        self._ahora = ahora  # Se inyecta para poder simular el paso del tiempo en las pruebas

    @classmethod
    def desde_settings(cls) -> "LoginBanService":
        """Crear el servicio con las variables de entorno y las tablas de la base de datos"""
        return cls(RepositorioBanSQLAlchemy(), ConfigBan())

    def esta_bloqueado(self, direccion_ip: str, email: str) -> ResultadoBan:
        """Consultar si la dirección IP o el email están bloqueados, no cuenta como intento"""
        direccion_ip, email = self._normalizar(direccion_ip, email)
        ahora = self._ahora()
        # Revisar del bloqueo más severo al menos severo
        bloqueos = sorted(self._repositorio.buscar_bloqueos_activos(direccion_ip, email), key=lambda b: b.tipo, reverse=True)
        for bloqueo in bloqueos:
            hasta = self._vigente_hasta(bloqueo)
            if bloqueo.tipo == TipoBan.SIEMPRE or ahora < hasta:
                return ResultadoBan(bloqueado=True, tipo=bloqueo.tipo, hasta=hasta)
            # Ya no está vigente, se da de baja
            self._repositorio.desactivar_bloqueo(bloqueo)
        return ResultadoBan(bloqueado=False)

    def registrar_intento_fallido(self, direccion_ip: str, email: str) -> ResultadoBan:
        """Sumar un intento fallido y bloquear si se llegó al máximo"""
        direccion_ip, email = self._normalizar(direccion_ip, email)
        ahora = self._ahora()
        # Tomar el contador, si es de otro día comienza de nuevo
        intento = self._repositorio.obtener_intento(direccion_ip, email)
        if intento is None:
            intento = Intento(id=None, direccion_ip=direccion_ip, email=email)
        elif intento.tiempo is None or intento.tiempo.date() != ahora.date():
            intento.intentos = 0
        intento.intentos += 1
        intento.tiempo = ahora
        # Si no llegó al máximo, solo se guarda el contador
        if intento.intentos < self._config.max_intentos:
            self._repositorio.guardar_intento(intento)
            return ResultadoBan(bloqueado=False, intentos=intento.intentos)
        # Llegó al máximo: por minutos, o para siempre si ya sobrepasó los bloqueos por minutos del día
        inicio_del_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        bloqueos_hoy = self._repositorio.contar_bloqueos(TipoBan.MINUTOS, direccion_ip, email, inicio_del_dia)
        tipo = TipoBan.SIEMPRE if bloqueos_hoy >= self._config.max_bloqueos_por_dia else TipoBan.MINUTOS
        bloqueo = self._repositorio.crear_bloqueo(Bloqueo(id=None, tipo=tipo, tiempo=ahora, direccion_ip=direccion_ip, email=email))
        # El contador vuelve a cero para la siguiente ronda
        intentos = intento.intentos
        intento.intentos = 0
        self._repositorio.guardar_intento(intento)
        return ResultadoBan(bloqueado=True, tipo=tipo, hasta=self._vigente_hasta(bloqueo), intentos=intentos)

    def registrar_acceso_exitoso(self, direccion_ip: str, email: str) -> None:
        """Al entrar con éxito, el contador de la pareja vuelve a cero"""
        direccion_ip, email = self._normalizar(direccion_ip, email)
        intento = self._repositorio.obtener_intento(direccion_ip, email)
        if intento is not None and intento.intentos != 0:
            intento.intentos = 0
            self._repositorio.guardar_intento(intento)

    def _vigente_hasta(self, bloqueo: Bloqueo) -> Optional[datetime]:
        """Fecha y hora en que caduca el bloqueo, None si es para siempre"""
        if bloqueo.tipo == TipoBan.MINUTOS:
            return bloqueo.tiempo + timedelta(minutes=self._config.duracion_minutos)
        if bloqueo.tipo == TipoBan.DIA:
            return datetime.combine(bloqueo.tiempo.date() + timedelta(days=1), datetime.min.time())
        return None

    @staticmethod
    def _normalizar(direccion_ip: str, email: str) -> tuple[str, str]:
        """Quitar espacios y pasar el email a minúsculas para que siempre coincidan los registros"""
        return (direccion_ip or "").strip()[:45], (email or "").strip().lower()[:256]


class RepositorioBanSQLAlchemy:
    """Repositorio con las tablas `ban_bloqueados` y `ban_intentos`"""

    def __init__(self):
        # Se importan aquí para que el servicio y sus pruebas no dependan de la base de datos
        # pylint: disable=import-outside-toplevel
        from ..blueprints.ban_bloqueados.models import BanBloqueado
        from ..blueprints.ban_intentos.models import BanIntento

        self._ban_bloqueado = BanBloqueado
        self._ban_intento = BanIntento

    def buscar_bloqueos_activos(self, direccion_ip: str, email: str) -> list[Bloqueo]:
        from sqlalchemy import or_  # pylint: disable=import-outside-toplevel

        modelo = self._ban_bloqueado
        condiciones = []
        if direccion_ip:
            condiciones.append(modelo.direccion_ip == direccion_ip)
        if email:
            condiciones.append(modelo.email == email)
        if not condiciones:
            return []
        registros = modelo.query.filter(modelo.estatus == "A").filter(or_(*condiciones)).all()
        return [self._a_bloqueo(registro) for registro in registros]

    def desactivar_bloqueo(self, bloqueo: Bloqueo) -> None:
        registro = self._ban_bloqueado.query.get(bloqueo.id)
        if registro is not None:
            registro.delete()

    def crear_bloqueo(self, bloqueo: Bloqueo) -> Bloqueo:
        registro = self._ban_bloqueado(
            ban_tipo_id=int(bloqueo.tipo),
            tiempo=bloqueo.tiempo,
            direccion_ip=bloqueo.direccion_ip or None,
            email=bloqueo.email or None,
        )
        registro.save()
        return self._a_bloqueo(registro)

    def contar_bloqueos(self, tipo: TipoBan, direccion_ip: str, email: str, desde: datetime) -> int:
        modelo = self._ban_bloqueado
        return (
            modelo.query.filter(modelo.ban_tipo_id == int(tipo))
            .filter(modelo.direccion_ip == direccion_ip)
            .filter(modelo.email == email)
            .filter(modelo.tiempo >= desde)
            .count()
        )

    def obtener_intento(self, direccion_ip: str, email: str) -> Optional[Intento]:
        registro = self._ban_intento.query.filter_by(direccion_ip=direccion_ip, email=email, estatus="A").first()
        if registro is None:
            return None
        return Intento(
            id=registro.id,
            direccion_ip=registro.direccion_ip,
            email=registro.email,
            intentos=registro.intentos,
            tiempo=registro.tiempo,
        )

    def guardar_intento(self, intento: Intento) -> Intento:
        registro = self._ban_intento.query.get(intento.id) if intento.id is not None else None
        if registro is None:
            registro = self._ban_intento(direccion_ip=intento.direccion_ip, email=intento.email)
        registro.intentos = intento.intentos
        registro.tiempo = intento.tiempo
        registro.save()
        intento.id = registro.id
        return intento

    @staticmethod
    def _a_bloqueo(registro) -> Bloqueo:
        return Bloqueo(
            id=registro.id,
            tipo=TipoBan(registro.ban_tipo_id),
            tiempo=registro.tiempo,
            direccion_ip=registro.direccion_ip,
            email=registro.email,
        )
